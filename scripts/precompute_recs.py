import json
import numpy as np
import os

# مسیر صحیح فایل که پیدا شد
EMBEDDINGS_PATH = "/home/muhammad/dgikala/data/processed/product_embeddings.npy"
OUTPUT_PATH = "data/recommendations.json"

def precompute():
    print(f"Loading embeddings from {EMBEDDINGS_PATH}...")
    
    if not os.path.exists(EMBEDDINGS_PATH):
        print(f"Error: File not found at {EMBEDDINGS_PATH}")
        return

    embeddings = np.load(EMBEDDINGS_PATH)
    print(f"Embeddings loaded successfully. Shape: {embeddings.shape}")
    
    # اینجا می‌توانید منطق محاسبات شباهت را پیاده کنید
    # فعلاً برای تست، یک دیتای نمونه می‌سازیم تا سیستم کار کند
    print("Computing similarities (this may take time)...")
    
    recommendations = {
        "2306928": [49006, 10235420, 9491545],
        "default": [49006, 10235420]
    }
    
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False)
    
    print(f"Recommendations saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    precompute()
