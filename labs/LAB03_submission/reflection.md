

| Genre | Part A Accuracy | Part B Accuracy |
|---|---|---|
| Animation | 0.827 | 0.873 |
| Comedy | 0.760 | 0.753 |
| Documentary | 0.847 | 0.827 |
| Horror | 0.780 | 0.780 |
| Romance | 0.693 | 0.740 |
| Sci-Fi | 0.653 | 0.720 |
| **Overall** | 0.760 | 0.782 |

Then address these questions:

1. **Architecture choices**: Describe the image branch and tabular branch architectures you settled on. Why did you choose this structure? What did you try that didn't work as well?
    The image branch used 4 convolutional blocks to downsample the image using max pooling. It halved the spatial size each time while the number of channels grew at the same rate. The first instinct was to flatten the poster image directly into a fully connected layer rather than using convolutional blocks. This didn't work because flattening a 128x128 image produces 49,152 inputs, creating far too many parameters for the network to learn meaningful patterns, and it immediately overfit without learning anything useful.

    The tabular branch has 2 sub branches, one for numeric features and the other for embedding the categorical data. It needed some way to combine the different data types and funnel them into the same output dimension. After both streams are combined into a 256 dim vector they pass through the final layer to produce the classification. We structured it this way because the different data types require different preprocessing steps before combining and making the final decision.


2. **Overfitting**: Did you observe a gap between training and validation accuracy? At what point did it appear? What strategies did you use to combat it (dropout, weight decay, early stopping, smaller vocabulary, reduced model size, learning rate scheduling)? Which were most effective?
    The model started overfitting around epoch 10, where training accuracy kept increasing but validation accuracy tapered off. To combat this, dropout was used to prevent the network from over relying on single features. The Adam optimizer with weight decay was also used to penalize large weights and reduce overfitting. The vocabulary size of 50 also limited the overfitting potential in the embedding layers, since a larger vocabulary would have meant more parameters with fewer training examples per token.

3. **Part A vs. Part B**: How did your custom CNN compare to the pretrained ResNet18? Did transfer learning help, and if so, in what way (higher accuracy, faster convergence, less overfitting)?
    The ResNet18 outperformed the custom CNN without requiring much additional work. The overall accuracy scores were 0.782 (ResNet18) and 0.760 (custom CNN). ResNet18 already had learned features from its previous training on 1.2 million ImageNet images, causing it to perform better out of the box. It achieved higher accuracy and reached convergence faster than the custom model. The biggest gains were in Romance (+0.047) and Sci-Fi (+0.067), suggesting those genres rely on more subtle visual patterns that the larger pretrained model captures better than a small custom CNN trained from scratch. 

4. **Tabular branch insights**: Which metadata features seemed most useful for genre prediction? Look at the per-class accuracy table — which genres did the model struggle with most? Does that make sense given the available features? If you tried ablations (tabular-only or image-only), what did you learn?
    Documentary had one of the highest scores in both models. Documentaries have very distinct features compared to other more traditional films, metadata like budget, MPAA rating, and cast members tend to be very different from other genres, making them easier to predict. Animation also scored high due to its visually distinct poster style and the fact that major production companies like Pixar appear frequently enough in the vocabulary to be predictive.

    Romance and SciFi scored the lowest. Romance posters and metadata values are very similar to Comedy and other genres, which is why it underperformed. SciFi struggled due to its wide range of values, budgets, runtimes, and ratings vary greatly across the genre. It also commonly overlapped with Horror, and without a consistent visual or metadata pattern the model had difficulty making accurate predictions.

 

5. **What would you do differently?** If you had more compute time or training data, what would you try next?
    Running the code on Google Colab presented some challenges, originally it had to load each image directly from Google Drive one at a time, causing a single epoch to take around 45 minutes. Once everything was copied into Colab's local storage, the entire training process took about 10 minutes. Beyond that, increasing the vocabulary size beyond 50 could improve performance since the model currently only tracks the most common names, meaning many genre predictive directors and cast members are mapped to unknown. Testing different dropout rates and learning rates could also yield better results. Finally, running more epochs with early stopping rather than a fixed epoch count would allow the model to train longer without risking additional overfitting.

6. *(Optional — only if you completed optional extensions)* **Optional extensions**: For each optional experiment you ran, briefly describe what you tried, what result you got, and how it compared to your Part A baseline.