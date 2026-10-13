import os
from src.utils.mlflow_logger import MLFlowTracker

def log_recommender_config():
    # ۱. تنظیمات و پارامترهایی که فعلاً در سیستم توصیه‌گر شما ثابت هستند
    params = {
        "algorithm": "ContentBased",
        "similarity_method": "cosine_similarity",
        "default_top_k": 5,
        "embedding_path": "data/processed/product_embeddings.npy",
        "description": "Baseline content-based recommender using product embeddings"
    }
    
    # ۲. متریک‌های خالی (چون فعلاً ارزیابی نداریم)
    metrics = {"status": 1.0} # نشان‌دهنده فعال بودن سرویس
    
    # ۳. ثبت در MLflow
    tracker = MLFlowTracker("Recommender_System")
    
    # ثبت به عنوان آرتیفکت اصلی (Embedding file)
    embedding_path = "data/processed/product_embeddings.npy"
    
    with open("temp_log.txt", "w") as f:
        f.write("Baseline Configuration for ContentRecommender")
    
    # استفاده از متد ثبت آرتیفکت
    tracker.log_evaluation_with_artifact(
        params=params,
        metrics=metrics,
        model_path=embedding_path if os.path.exists(embedding_path) else "temp_log.txt"
    )
    
    if os.path.exists("temp_log.txt"):
        os.remove("temp_log.txt")

if __name__ == "__main__":
    log_recommender_config()
