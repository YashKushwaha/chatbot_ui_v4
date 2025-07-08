import os
from PIL import Image
from fastapi.responses import FileResponse

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
        
    def get_image_response(self, filename: str):
        full_path = os.path.join(self.image_folder, filename)
        if os.path.exists(full_path):
            return FileResponse(full_path, media_type="image/jpeg")  # or infer from extension
        else:
            return None
        
