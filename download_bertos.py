#!/usr/bin/env python3
import os
import tarfile
import requests
from pathlib import Path

def download_bertos():
    """Download and extract BERTOS data."""
    # BERTOS URL
    bertos_url = "https://figshare.com/ndownloader/files/52231394"
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Download file
    print("Downloading BERTOS data...")
    response = requests.get(bertos_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    file_path = data_dir / "bertos.tar.gz"
    block_size = 1024
    downloaded = 0
    
    with open(file_path, 'wb') as file:
        for data in response.iter_content(block_size):
            downloaded += len(data)
            file.write(data)
            if total_size > 0:
                percentage = (downloaded / total_size) * 100
                print(f"\rProgress: {percentage:.1f}%", end='')
    
    print("\nDownload complete!")
    
    # Extract the file
    print("Extracting BERTOS data...")
    bertos_dir = data_dir / 'bertos'
    bertos_dir.mkdir(exist_ok=True)
    
    with tarfile.open(file_path, 'r:gz') as tar:
        tar.extractall(path=bertos_dir)
    
    print(f"Done! BERTOS files are in: {bertos_dir}")

if __name__ == "__main__":
    download_bertos()