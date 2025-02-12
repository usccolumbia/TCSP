#!/usr/bin/env python3
import os
import tarfile
import requests
from pathlib import Path

def download_bertos():
    """Download and extract BERTOS data into the current directory."""
    # BERTOS URL
    bertos_url = "https://figshare.com/ndownloader/files/52231394"
    
    # Define paths
    file_path = Path("bertos.tar.gz")
    extract_temp_dir = Path("BERTOS_temp")  # Temporary extraction directory
    bertos_dir = Path("BERTOS")  # Final directory

    # Download file
    print("Downloading BERTOS data...")
    response = requests.get(bertos_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
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

    # Extract to a temporary directory
    print("Extracting BERTOS data...")
    
    extract_temp_dir.mkdir(exist_ok=True)
    
    with tarfile.open(file_path, 'r:gz') as tar:
        tar.extractall(path=extract_temp_dir)

    # Move extracted files to the correct location
    extracted_subdir = extract_temp_dir / "BERTOS"
    if extracted_subdir.exists():
        # Move contents to the final BERTOS directory
        if bertos_dir.exists():
            os.system(f"rm -rf {bertos_dir}")  # Ensure it's clean
        extracted_subdir.rename(bertos_dir)
    else:
        extract_temp_dir.rename(bertos_dir)  # If the archive didn't have a nested BERTOS dir

    # Clean up
    file_path.unlink()  # Remove the tar.gz file
    if extract_temp_dir.exists():
        os.rmdir(extract_temp_dir)  # Remove temp dir if empty

    print(f"Done! BERTOS is available at: {bertos_dir.resolve()}")

if __name__ == "__main__":
    download_bertos()
