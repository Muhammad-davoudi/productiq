import json
import os
from src.utils.mlflow_logger import MLFlowTracker

def split_metrics_and_params(data_dict):
    metrics = {}
    params = {}
    for k, v in data_dict.items():
        if isinstance(v, (int, float)):
            metrics[k] = v
        else:
            params[k] = str(v)
    return metrics, params

def log_existing_data():
    # ۱. ثبت نتایج NLP
    if os.path.exists("data/processed/nlp_evaluation.json"):
        with open("data/processed/nlp_evaluation.json", "r") as f:
            nlp_data = json.load(f)
        m_nlp, p_nlp = split_metrics_and_params(nlp_data)
        p_nlp.update({"source": "baseline_evaluation"})
        tracker = MLFlowTracker("NLP_Sentiment_Model")
        tracker.log_evaluation_with_artifact(params=p_nlp, metrics=m_nlp, model_path="models/sentiment_model.pkl")

    # ۲. ثبت نتایج Clustering
    if os.path.exists("data/processed/clustering_evaluation.json"):
        with open("data/processed/clustering_evaluation.json", "r") as f:
            cluster_data = json.load(f)
        m_clust, p_clust = split_metrics_and_params(cluster_data)
        p_clust.update({"source": "baseline_evaluation"})
        tracker = MLFlowTracker("Clustering_Model")
        tracker.log_evaluation_with_artifact(params=p_clust, metrics=m_clust, model_path="models/kmeans_product_model.joblib")

    # ۳. ثبت نتایج Recommender
    if os.path.exists("data/processed/recommender_evaluation.json"):
        with open("data/processed/recommender_evaluation.json", "r") as f:
            rec_data = json.load(f)
        m_rec, p_rec = split_metrics_and_params(rec_data)
        p_rec.update({"source": "baseline_evaluation"})
        tracker = MLFlowTracker("Recommender_System")
        # توجه: اگر نام فایل مدل شما متفاوت است، مسیر زیر را تغییر دهید
        tracker.log_evaluation_with_artifact(params=p_rec, metrics=m_rec, model_path="models/recommender_model.pkl")
    else:
        print("Warning: Recommender evaluation file not found, skipping.")

if __name__ == "__main__":
    log_existing_data()
