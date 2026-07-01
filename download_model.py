import os
import requests
import re

def download_from_google_drive(file_id, destination):
    print(f"Downloading file ID: {file_id}")
    
    # URL for confirmation page
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    
    session = requests.Session()
    response = session.get(url, stream=True)
    
    # Get confirmation token if needed
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            print("Confirmation token found, processing...")
            params = {'id': file_id, 'confirm': value}
            response = session.get('https://drive.google.com/uc', params=params, stream=True)
            break
    
    # Save file
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    
    # Verify file size
    file_size = os.path.getsize(destination)
    print(f"Downloaded: {destination} ({file_size} bytes)")
    return destination

FILE_ID = "1LeYuYnY6tAr1qR7Jke7qOPkLt8Ue2yrY"
MODEL_PATH = "app/models/maize_disease_model.h5"

print("Downloading model from Google Drive...")
download_from_google_drive(FILE_ID, MODEL_PATH)

# Verify file is valid HDF5
import h5py
try:
    with h5py.File(MODEL_PATH, 'r') as f:
        print("✅ File is valid HDF5 format")
        print(f"   Keys: {list(f.keys())}")
except Exception as e:
    print(f"❌ Invalid HDF5 file: {e}")
