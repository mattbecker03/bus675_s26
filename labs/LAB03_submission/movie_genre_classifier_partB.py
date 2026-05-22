"""
Lab 3 — Part B: ResNet18 Drop-In Image Branch
==============================================
Identical to Part A except ImageBranch uses a frozen pretrained ResNet18
backbone. Everything else (Dataset, TabularBranch, FusionHead, training)
is unchanged.
"""

import json
import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm


# =============================================================================
# Constants
# =============================================================================

GENRES = ["Animation", "Comedy", "Documentary", "Horror", "Romance", "Sci-Fi"]

NUMERIC_COLS = ["runtime", "vote_average", "vote_count",
                "release_year", "popularity", "budget", "revenue"]

LIST_FIELDS       = ["cast", "directors", "writers", "production_companies"]
SINGLE_CAT_FIELDS = ["mpaa_rating"]

IMAGE_SIZE   = 128
MAX_LIST_LEN = 20
TOP_N_VOCAB  = 50
EMBED_DIM    = 32

DATA_DIR  = Path("../data/movie_posters")
IMAGE_DIR = DATA_DIR / "images"

CHECKPOINT_PATH = "best_model_partB.pth"


# =============================================================================
# PROVIDED: VocabBuilder
# =============================================================================

class VocabBuilder:
    PAD_IDX = 0
    UNK_IDX = 1

    def __init__(self, top_n=TOP_N_VOCAB):
        self.top_n  = top_n
        self.vocabs = {}
        self.sizes  = {}

    def fit(self, df):
        for field in LIST_FIELDS:
            if field not in df.columns:
                continue
            counts = Counter()
            for val in df[field].dropna():
                if val:
                    counts.update(v.strip() for v in str(val).split("|") if v.strip())
            top_tokens = [tok for tok, _ in counts.most_common(self.top_n)]
            vocab = {tok: idx + 2 for idx, tok in enumerate(top_tokens)}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2

        for field in SINGLE_CAT_FIELDS:
            if field not in df.columns:
                continue
            unique_vals = [v for v in df[field].unique()
                           if isinstance(v, str) and v.strip()]
            vocab = {v: idx + 2 for idx, v in enumerate(sorted(unique_vals))}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2
        return self

    def encode_list(self, val, field, max_len=MAX_LIST_LEN):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return [self.PAD_IDX] * max_len
        tokens = [v.strip() for v in val.split("|") if v.strip()]
        ids = [vocab.get(tok, self.UNK_IDX) for tok in tokens]
        ids = ids[:max_len]
        ids += [self.PAD_IDX] * (max_len - len(ids))
        return ids

    def encode_single(self, val, field):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return self.PAD_IDX
        return vocab.get(val.strip(), self.UNK_IDX)

    def save(self, path):
        data = {"vocabs": self.vocabs, "sizes": self.sizes, "top_n": self.top_n}
        Path(path).write_text(json.dumps(data))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        vb = cls(top_n=data["top_n"])
        vb.vocabs = data["vocabs"]
        vb.sizes  = data["sizes"]
        return vb


# =============================================================================
# PROVIDED: NumericScaler
# =============================================================================

class NumericScaler:
    def __init__(self):
        self.means = {}
        self.stds  = {}

    def fit(self, df):
        for col in NUMERIC_COLS:
            if col in df.columns:
                vals = pd.to_numeric(df[col], errors="coerce")
                self.means[col] = float(vals.mean())
                self.stds[col]  = max(float(vals.std()), 1e-8)
        return self

    def transform(self, df):
        result = {}
        for col in NUMERIC_COLS:
            vals = pd.to_numeric(df[col], errors="coerce") if col in df.columns \
                   else pd.Series([float("nan")] * len(df))
            vals = vals.fillna(self.means.get(col, 0.0))
            mean = self.means.get(col, 0.0)
            std  = self.stds.get(col, 1.0)
            result[col] = ((vals - mean) / std).values.astype(np.float32)
        return result

    def save(self, path):
        Path(path).write_text(json.dumps({"means": self.means, "stds": self.stds}))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        ns = cls()
        ns.means = data["means"]
        ns.stds  = data["stds"]
        return ns


# =============================================================================
# Dataset  (identical to Part A)
# =============================================================================

class MoviePosterDataset(Dataset):
    def __init__(self, df, image_dir, vocab_builder, numeric_scaler, transform=None):
        self.df            = df.reset_index(drop=True)
        self.image_dir     = Path(image_dir)
        self.vocab_builder = vocab_builder
        self.transform     = transform

        scaled = numeric_scaler.transform(df)
        self.numeric = np.stack([scaled[col] for col in NUMERIC_COLS], axis=1)
        self.labels  = [GENRES.index(g) for g in df["label"]]

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        img_path = self.image_dir / row["image_path"].split("/")[-1]
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception:
            image = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE))
        if self.transform:
            image = self.transform(image)

        numeric = torch.tensor(self.numeric[idx], dtype=torch.float32)

        sample = {"image": image, "numeric": numeric, "label": torch.tensor(self.labels[idx])}
        for field in LIST_FIELDS:
            ids = self.vocab_builder.encode_list(row.get(field, ""), field)
            sample[field] = torch.tensor(ids, dtype=torch.long)

        sample["mpaa_rating"] = torch.tensor(
            self.vocab_builder.encode_single(row.get("mpaa_rating", ""), "mpaa_rating"),
            dtype=torch.long,
        )

        return sample


# =============================================================================
# Image Branch — ResNet18 (replaces Part A's custom CNN)
# =============================================================================

class ImageBranch(nn.Module):
    """
    Transfer learning image encoder: pretrained ResNet18 backbone
    with a small trainable projection head. Backbone weights are frozen.
    """

    BACKBONE_OUT_DIM = 512

    def __init__(self, out_dim=256, dropout=0.4, fine_tune=False):
        super().__init__()

        backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        for param in backbone.parameters():
            param.requires_grad = False

        if fine_tune:
            for param in backbone.layer4.parameters():
                param.requires_grad = True

        self.backbone = nn.Sequential(*list(backbone.children())[:-1])

        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(self.BACKBONE_OUT_DIM, out_dim),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        features = self.backbone(x)
        return self.head(features)


# =============================================================================
# Tabular Branch  (identical to Part A)
# =============================================================================

class TabularBranch(nn.Module):
    def __init__(self, vocab_sizes, out_dim=256, dropout=0.3):
        super().__init__()
        all_fields = LIST_FIELDS + SINGLE_CAT_FIELDS
        self.embeddings = nn.ModuleDict({
            field: nn.Embedding(vocab_sizes[field], EMBED_DIM, padding_idx=0)
            for field in all_fields if field in vocab_sizes
        })
        emb_input_dim = EMBED_DIM * len(self.embeddings)
        self.emb_mlp = nn.Sequential(
            nn.Linear(emb_input_dim, 128), nn.ReLU(inplace=True), nn.Dropout(dropout),
        )
        self.num_mlp = nn.Sequential(
            nn.Linear(len(NUMERIC_COLS), 64), nn.ReLU(inplace=True),
            nn.Linear(64, 128),              nn.ReLU(inplace=True), nn.Dropout(dropout),
        )
        self.merge = nn.Sequential(
            nn.Linear(128 + 128, out_dim), nn.ReLU(inplace=True),
        )

    def _pool_embedding(self, emb_layer, ids):
        emb = emb_layer(ids)
        if ids.dim() == 1:
            return emb
        mask = (ids != 0).float().unsqueeze(-1)
        n    = mask.sum(dim=1).clamp(min=1)
        return (emb * mask).sum(dim=1) / n

    def forward(self, numeric, cat_fields):
        pooled = []
        for field in LIST_FIELDS:
            if field in self.embeddings:
                pooled.append(self._pool_embedding(self.embeddings[field], cat_fields[field]))
        for field in SINGLE_CAT_FIELDS:
            if field in self.embeddings:
                pooled.append(self._pool_embedding(self.embeddings[field], cat_fields[field]))
        emb_vec = self.emb_mlp(torch.cat(pooled, dim=1))
        num_vec = self.num_mlp(numeric)
        return self.merge(torch.cat([emb_vec, num_vec], dim=1))


# =============================================================================
# Fusion Head  (identical to Part A)
# =============================================================================

class FusionHead(nn.Module):
    def __init__(self, image_dim, tabular_dim, num_classes=len(GENRES), dropout=0.4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(image_dim + tabular_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes),
        )

    def forward(self, image_features, tabular_features):
        return self.net(torch.cat([image_features, tabular_features], dim=1))


# =============================================================================
# Full Model  (identical to Part A)
# =============================================================================

class MultimodalGenreClassifier(nn.Module):
    IMG_DIM = 256
    TAB_DIM = 256

    def __init__(self, vocab_sizes):
        super().__init__()
        self.image_branch   = ImageBranch(out_dim=self.IMG_DIM)
        self.tabular_branch = TabularBranch(vocab_sizes, out_dim=self.TAB_DIM)
        self.fusion_head    = FusionHead(self.IMG_DIM, self.TAB_DIM)

    def forward(self, image, numeric, cat_fields):
        img_feats = self.image_branch(image)
        tab_feats = self.tabular_branch(numeric, cat_fields)
        return self.fusion_head(img_feats, tab_feats)


# =============================================================================
# Training helpers  (identical to Part A)
# =============================================================================

def build_transforms(train=True):
    if train:
        return transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])


def extract_batch(batch, device):
    image      = batch["image"].to(device)
    numeric    = batch["numeric"].to(device)
    label      = batch["label"].to(device)
    cat_fields = {f: batch[f].to(device) for f in LIST_FIELDS + SINGLE_CAT_FIELDS}
    return image, numeric, cat_fields, label


def evaluate(model, loader, device):
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for batch in loader:
            image, numeric, cat_fields, label = extract_batch(batch, device)
            preds = model(image, numeric, cat_fields).argmax(dim=1)
            correct += (preds == label).sum().item()
            total   += label.size(0)
    return correct / total


def per_class_accuracy(model, loader, device):
    model.eval()
    correct = [0] * len(GENRES)
    totals  = [0] * len(GENRES)
    with torch.no_grad():
        for batch in loader:
            image, numeric, cat_fields, label = extract_batch(batch, device)
            preds = model(image, numeric, cat_fields).argmax(dim=1)
            for i in range(len(GENRES)):
                mask        = label == i
                correct[i] += (preds[mask] == label[mask]).sum().item()
                totals[i]  += mask.sum().item()
    return {g: (correct[i] / totals[i] if totals[i] > 0 else 0.0)
            for i, g in enumerate(GENRES)}


def train(data_dir=None, image_dir=None, epochs=15, batch_size=64, lr=1e-3):
    d   = Path(data_dir)  if data_dir  else DATA_DIR
    img = Path(image_dir) if image_dir else IMAGE_DIR

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    tmp = ImageBranch()
    trainable = sum(p.numel() for p in tmp.parameters() if p.requires_grad)
    frozen    = sum(p.numel() for p in tmp.parameters() if not p.requires_grad)
    print(f"Image branch — trainable: {trainable:,}  frozen: {frozen:,}")
    del tmp

    train_df = pd.read_csv(d / "train_manifest.csv")
    val_df   = pd.read_csv(d / "val_manifest.csv")
    test_df  = pd.read_csv(d / "test_manifest.csv")
    print(f"Train: {len(train_df):,}  Val: {len(val_df):,}  Test: {len(test_df):,}")

    vocab_builder  = VocabBuilder().fit(train_df)
    numeric_scaler = NumericScaler().fit(train_df)

    train_ds = MoviePosterDataset(train_df, img, vocab_builder, numeric_scaler,
                                  transform=build_transforms(train=True))
    val_ds   = MoviePosterDataset(val_df,   img, vocab_builder, numeric_scaler,
                                  transform=build_transforms(train=False))
    test_ds  = MoviePosterDataset(test_df,  img, vocab_builder, numeric_scaler,
                                  transform=build_transforms(train=False))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=2, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False,
                              num_workers=2, pin_memory=True)
    test_loader  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False,
                              num_workers=2, pin_memory=True)

    model     = MultimodalGenreClassifier(vocab_builder.sizes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = correct = total = 0

        for batch in tqdm(train_loader, desc=f"Epoch {epoch}/{epochs}", leave=False):
            image, numeric, cat_fields, label = extract_batch(batch, device)
            optimizer.zero_grad()
            logits = model(image, numeric, cat_fields)
            loss   = criterion(logits, label)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * label.size(0)
            preds       = logits.argmax(dim=1)
            correct    += (preds == label).sum().item()
            total      += label.size(0)

        scheduler.step()
        train_acc = correct / total
        val_acc   = evaluate(model, val_loader, device)

        print(f"Epoch {epoch:02d} | loss {total_loss/total:.4f} | "
              f"train acc {train_acc:.3f} | val acc {val_acc:.3f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                "epoch":                epoch,
                "model_state_dict":     model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc":              val_acc,
            }, CHECKPOINT_PATH)
            print(f"  -> Saved checkpoint (val acc {val_acc:.3f})")

    print(f"\nBest validation accuracy: {best_val_acc:.3f}")

    checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    per_class = per_class_accuracy(model, test_loader, device)
    overall   = sum(per_class.values()) / len(per_class)

    print("\n=== Per-Class Test Accuracy (Part B) ===")
    for genre, acc in per_class.items():
        print(f"  {genre:<15} {acc:.3f}")
    print(f"  {'Overall':<15} {overall:.3f}")


if __name__ == "__main__":
    train(
        data_dir="/content/Lab03_local",
        image_dir="/content/Lab03_local/images",
    )
