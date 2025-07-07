from pathlib import Path
import os
from datasets import load_dataset
from pymongo import MongoClient, ASCENDING, UpdateOne
import hashlib
import chromadb

def download_flickr30k_dataset(dataset_name, download_location=None):
    dataset = load_dataset(dataset_name, cache_dir=download_location)
    return dataset

def create_dataset_summary(dataset, dataset_name, download_location):
    data_folder_name = dataset_name.replace("/", "___")
    summary_path = os.path.join(download_location, f"{data_folder_name}_dataset_summary.txt")
    # Example summary
    with open(summary_path, "w") as f:
        f.write(f"Dataset: {dataset_name}\n")
        f.write(f"Available Splits:\n")
        
        for split in dataset.keys():
            num_records = len(dataset[split])
            f.write(f"  - {split}: {num_records} records\n")
        

if __name__ == '__main__':

    CACHE_DIR = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "data")
    os.makedirs(CACHE_DIR, exist_ok=True)
    DATASET_NAME = "nlphuji/flickr30k"
    dataset = download_flickr30k_dataset(dataset_name = DATASET_NAME, download_location = CACHE_DIR)

    create_dataset_summary(dataset, dataset_name = DATASET_NAME, download_location = CACHE_DIR)  
