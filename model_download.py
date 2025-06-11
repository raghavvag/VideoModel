import os
import boto3
import botocore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def download_models():
    """Download model files from S3 if they don't exist locally"""
    # Create weights directory if it doesn't exist
    os.makedirs('weights', exist_ok=True)
    
    # Check if we need to download the model
    if not os.path.exists('weights/model.pt'):
        print("Downloading model file from storage...")
        try:
            # Initialize S3 client
            s3 = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            
            # Download model file
            s3.download_file(
                os.environ.get('S3_BUCKET_NAME', 'your-bucket-name'),
                'model.pt',
                'weights/model.pt'
            )
            print("Model downloaded successfully")
        except botocore.exceptions.ClientError as e:
            print(f"Error downloading model: {e}")
            return False
    return True
