# Lab 2 Submission README

## Student Information
- Name: Matthew Becker
- Date: [2026-04-02]

## Deliverables Included
- `inference_api/Dockerfile`
- `preprocessor/Dockerfile`
- `inference_api/app.py` (with `/health` and `/stats`)
- `sample_classifications_20.jsonl` (first 20 lines from logs)
- `Reflection.md`

## Docker Build Commands Used

### Inference API
```bash
cd LAB02_submission/inference_api
docker build -t congo-inference-api .
```

### Preprocessor
```bash
cd LAB02_submission/preprocessor
docker build -t congo-preprocessor
```

## Docker Run Commands Used

### Inference API Container
```bash
cd LAB02_submission/inference_api
docker run -d \
  --name congo-inference-api \
  -p 8000:8000 \
  -v "$(pwd)/logs:/logs" \
  congo-inference-api
```

### Preprocessor Container
```bash
cd LAB02_submission
docker run -d \
  --name congo-preprocessor \
  -v "$(pwd)/incoming:/incoming" \
  -e API_URL=http://host.docker.internal:8000 \
  congo-preprocessor
```

## Brief Explanation: How the Containers Communicate
[Write 3-6 sentences here.]
The preprocessor container monitors /incoming folder for new images to classify.
When a new image enter it, the watcher.py file extracts customer_id and product_id to the inference api and uses /predict from the app.py to its endpoint. The preprocessor knows where to find the inference API using the API_URL = os.environ.get("API_URL", "http://localhost:8000"). The API published a port 8000 on the host machine and lets the preprocessor talk to the host from inside the docker file. The mounted host folders allow the image and log to persist outside the container, the preprocessor is able to read images from the incoming folder and the interence api file can write to the log folder. Localhost can be weird because it refers to itself rather than the host machine or another container.

    

Points to cover:
- Which container calls which endpoint.
- How the preprocessor knows where to find the inference API.
- How images and logs persist using mounted host folders.
- Why `localhost` can be tricky inside containers.

