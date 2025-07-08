import torch
import open_clip
from PIL import Image

class OpenCLIPEmbedder:
    def __init__(self, model_name="ViT-L-14", pretrained="laion2b_s32b_b82k", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.model = self.model.to(self.device)
    
    def encode_text(self, texts, normalize=True):
        if isinstance(texts, str):
            texts = [texts]
        
        tokens = self.tokenizer(texts).to(self.device)
        with torch.no_grad():
            features = self.model.encode_text(tokens)
        if normalize:
            features /= features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy()
    
    def encode_image(self, images, normalize=True):
        if isinstance(images, str):
            images = [Image.open(images)]
        elif isinstance(images, Image.Image):
            images = [images]
        
        images = torch.stack([self.preprocess(img) for img in images]).to(self.device)
        with torch.no_grad():
            features = self.model.encode_image(images)
        if normalize:
            features /= features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy()
