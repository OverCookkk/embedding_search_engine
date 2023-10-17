import torch
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"


# 中文版本的clip
class CnClipEncodeModel:
    def __init__(self):
        self.model, self.preprocess = load_from_name("ViT-B-16", device=device, download_root='./deploy')
        self.model.eval()
        print("Available models:", available_models())
        # Available models: ['ViT-B-16', 'ViT-L-14', 'ViT-L-14-336', 'ViT-H-14', 'RN50']

    def extract_image_features(self, path):
        image_data = self.preprocess(Image.open(path)).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_data)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy()[0]  # [1, 1024]

    def extract_text_features(self, text):
        text_data = clip.tokenize(text).to(device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_data)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy()[0]  # [1, 1024]
