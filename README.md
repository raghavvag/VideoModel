# DeepFake Detection API

A machine learning API that analyzes videos to detect deepfakes using face recognition and EfficientNet models.

## Features

- Analyzes video files to detect potential deepfakes
- Provides a confidence score (0-1) for deepfake probability
- Supports MP4, AVI, and MOV video formats
- Handles face detection and analysis
- REST API with easy integration

## API Usage

### Endpoint: /detect

**Method:** POST

**Request:**
- Form-data with a video file (key: "file")

**Response:**
```json
{
    "score": 0.85,
    "is_deepfake": true
}
```

## Deployment Notes

This application uses Git LFS for storing large model files. Make sure to install Git LFS before cloning this repository.

```bash
git lfs install
git clone [repository-url]
```

## Requirements

See requirements.txt for complete dependencies.
