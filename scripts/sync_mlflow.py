import os
from src.utils.mlflow_logger import MLFlowTracker

def sync_all():
    tracker = MLFlowTracker(experiment_name="digikala_production_sync")
    
    # 1. Sentiment Model (if exists)
    sentiment_path = "models/sentiment_model.pkl"
    if not os.path.exists(sentiment_path):
        sentiment_path = "models/baseline_sentiment.joblib"
        
    if os.path.exists(sentiment_path):
        p_nlp = {"model_type": "sentiment", "status": "synced"}
        m_nlp = {"synced_status": 1.0}
        tracker.log_evaluation_with_artifact(params=p_nlp, metrics=m_nlp, model_path=sentiment_path)
        print(f"Logged sentiment model from {sentiment_path}")
    else:
        print("Warning: No sentiment model found.")

    # 2. Clustering Model
    cluster_path = "models/online_cluster_classifier.joblib"
    if os.path.exists(cluster_path):
        p_clust = {"model_type": "online_clustering", "status": "synced"}
        m_clust = {"synced_status": 1.0}
        tracker.log_evaluation_with_artifact(params=p_clust, metrics=m_clust, model_path=cluster_path)
        print(f"Logged clustering model from {cluster_path}")
    else:
        print("Warning: Clustering model not found.")

if __name__ == "__main__":
    sync_all()
