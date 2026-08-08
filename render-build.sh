#!/bin/bash
# exit on error
set -o errexit

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt

echo "--- Downloading model from Google Drive ---"

FILE_ID="1LeYuYnY6tAr1qR7Jke7qOPkLt8Ue2yrY"
DESTINATION="app/models/maize_disease_model.h5"

mkdir -p app/models

gdown --fuzzy "https://drive.google.com/uc?id=${FILE_ID}" -O ${DESTINATION}


if [ -f "$DESTINATION" ]; then
    echo "? Model downloaded successfully!"
    ls -lh $DESTINATION
else
    echo "? Failed to download model."
    exit 1
fi

echo "--- Build completed ---"