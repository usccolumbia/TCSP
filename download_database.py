#!/usr/bin/env python3
import os
import tarfile
import requests
from pathlib import Path

def download_file(url, filename):
    """Download a file from a URL with a progress indicator."""
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    file_path = os.path.join('data', filename)
    block_size = 1024  # 1 KB
    downloaded = 0
    
    with open(file_path, 'wb') as file:
        for data in response.iter_content(block_size):
            downloaded += len(data)
            file.write(data)
            
            # Calculate progress
            if total_size > 0:
                percentage = (downloaded / total_size) * 100
                print(f"\rProgress: {percentage:.1f}%", end='')
    print("\nDownload complete!")
    return file_path

def extract_targz(file_path):
    """Extract a .tar.gz file."""
    print(f"Extracting {file_path}...")
    with tarfile.open(file_path, 'r:gz') as tar:
        tar.extractall(path='data')
    print("Extraction complete!")

def main():
    # URLs for the data files
    cif_url = "https://figshare.com/ndownloader/files/52230974"
    csv_url = "https://figshare.com/ndownloader/files/52230977"
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Download files
    cif_file = download_file(cif_url, "structures.tar.gz")
    csv_file = download_file(csv_url, "data.csv")
    
    # Extract the tar.gz file
    extract_targz(cif_file)
    
    print("\nSetup complete! Files are stored in the 'data' directory.")
    print(f"CSV file: {csv_file}")
    print(f"CIF files: {data_dir}/structures/")

if __name__ == "__main__":
    main()