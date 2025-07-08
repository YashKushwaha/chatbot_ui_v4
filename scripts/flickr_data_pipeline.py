from pathlib import Path
import os
from datasets import load_dataset
from pymongo import MongoClient, ASCENDING, UpdateOne
import hashlib
import chromadb
from PIL import Image

from src.embedding_model import  OpenCLIPEmbedder

def get_mongo_db_client():
    client = MongoClient("mongodb://localhost:27017/")
    assert client.admin.command("ping") == {'ok': 1.0}
    return client

CHROMA_DB_PORT = '8010'

def get_chroma_db_client():
    client = chromadb.HttpClient(
        host="localhost",
        port=int(CHROMA_DB_PORT))
    return client


class FLICKR:
    def __init__(self, dataset_split):
        self.dataset_split = dataset_split
    def __iter__(self):
        for record in self.dataset_split:
            yield record
    def batch(self, batch_size):
        """
        Yield records in batches of batch_size
        """
        batch = []
        for record in self:
            batch.append(record)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch  # Yield remaining records if any

def upload_data_to_mongo_db(dataset):
    mongo_db_client = get_mongo_db_client()
    
    database = mongo_db_client['chatbot_ui_v4']  

    caption_collection = database['caption']
    caption_collection.create_index([("sent_id", ASCENDING)], unique=True)

    #images_collection = database['images']
    #images_collection.create_index([("img_id", ASCENDING)], unique=True)

    iterator = FLICKR(dataset)
    print('Done with records:')
    batch_size = 32
    counter = 0
    for batch in iterator.batch(batch_size=batch_size):
        final_records = []
        for record in batch:
            to_append = [{'sent_id': sent_id, 'caption': caption} for sent_id, caption in zip(record['sentids'],record['caption'])]
            to_append = [dict(**i, img_id=record['img_id'], filename = record['filename']) for i in to_append]
            final_records.extend(to_append)
        
        records = [UpdateOne({'sent_id': i['sent_id']}, {'$set': i}, upsert=True) for i in final_records]
        caption_collection.bulk_write(records)

        counter+=batch_size
        if counter % (10*batch_size) == 0:
            print(counter, end='\t')



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
        
def upload_data_to_chroma_db(dataset, embed_model):
    vec_db_client = get_chroma_db_client()
    
    images_collection = vec_db_client.get_or_create_collection('images')

    iterator = FLICKR(dataset)
    print('Done with records:')
    batch_size = 64
    counter = 0
    for batch in iterator.batch(batch_size=batch_size):
        images = [i['image'] for i in batch]
        
        embeddings = embed_model.encode_image(images)
        documents = [i['filename'] for i in batch]
        ids = [i['img_id'] for i in batch]

        to_upload = dict(documents=documents, embeddings=embeddings, ids=ids)
        images_collection.add(**to_upload)
        
        counter+=batch_size
        if counter % (10*batch_size) == 0:
            print(counter, end='\t')


class ImageStore:
    '''
    This class handles the images in flickr30k dataset
    '''
    def __init__(self, image_folder):
        self.image_folder = image_folder
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
            print('Folder created -> ', self.image_folder)
    
    def create_image_dataset(self, hf_dataset):
        '''
        The dataset from huggingface contains records as dictionary object where images are saved as PIL objects
        We need to save these images on the disk
        '''
        for record in hf_dataset:
            image = record['image']
            filename = record['filename']

            save_name = os.path.join(self.image_folder, filename)
            if not os.path.exists(save_name):
                image.save(save_name) 

    def get_image(self, filename):
        full_path = os.path.join(self.image_folder, filename)
        if os.path.exists(full_path):
            return Image.open(full_path)
        else:
            return None

if __name__ == '__main__':

    CACHE_DIR = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "data")
    os.makedirs(CACHE_DIR, exist_ok=True)
    DATASET_NAME = "nlphuji/flickr30k"
    dataset = download_flickr30k_dataset(dataset_name = DATASET_NAME, download_location = CACHE_DIR)
    dataset = dataset['test']
    create_dataset_summary(dataset, dataset_name = DATASET_NAME, download_location = CACHE_DIR)  

    image_folder_location = os.path.join(CACHE_DIR, 'images')

    image_store = ImageStore(image_folder_location)
    image_store.create_image_dataset(dataset)
      
    upload_data_to_mongo_db(dataset)
    embed_model = OpenCLIPEmbedder(device='cuda')
    upload_data_to_chroma_db(dataset = dataset['test'], embed_model=embed_model)

