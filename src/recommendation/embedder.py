import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

class ProductEmbedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        
    def create_product_text(self, df):
        # استفاده از نام ستون‌های واقعی فایل CSV شما
        text_cols = ['title_fa', 'Category1', 'Brand']
        return df[text_cols].fillna('').agg(' '.join, axis=1)

    def generate_embeddings(self, df):
        texts = self.create_product_text(df).tolist()
        return self.model.encode(texts, show_progress_bar=True, batch_size=32)

    def save_embeddings(self, embeddings, output_path='data/processed/product_embeddings.npy'):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        np.save(output_path, embeddings)

    def load_embeddings(self, input_path='data/processed/product_embeddings.npy'):
        return np.load(input_path)
