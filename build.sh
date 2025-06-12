#!/bin/bash
# Install system dependencies for OpenCV
apt-get update
apt-get install -y libgl1-mesa-glx libglib2.0-0
# Install Python dependencies
pip install -r requirements.txt
# Create necessary directories
mkdir -p weights temp
