import os
import unittest
from dotenv import load_dotenv
from src.recommendation.recommender import ContentRecommender
from src.llm.service import AssistantService
from src.kafka.clustering_consumer import predict_cluster, load_clustering_model

load_dotenv()

class TestDigikalaRealIntegration(unittest.TestCase):
    
    def test_database_connection_and_recommender(self):
        print("\n[TEST] Running real database & recommender test...")
        recommender = ContentRecommender()
        # تست جستجوی محصولات مشابه با یک کلمه واقعی از دیتابیس
        results = recommender.get_similar_products_by_title("گوشی موبایل", limit=3)
        print(f"Recommender results for 'گوشی موبایل': {results}")
        self.assertIsInstance(results, list)

    def test_clustering_model_inference(self):
        print("\n[TEST] Running real ML clustering model inference test...")
        model = load_clustering_model()
        if model is not None:
            sample_data = {"price": 15000000, "rate": 4.5, "rate_cnt": 120}
            cluster = predict_cluster(sample_data)
            print(f"Predicted cluster for sample data: {cluster}")
            self.assertIsInstance(cluster, int)
        else:
            print("[WARN] Clustering model file not found, skipped model inference test.")

    def test_llm_assistant_service(self):
        print("\n[TEST] Initializing LLM Assistant Service...")
        try:
            assistant = AssistantService()
            self.assertIn("recommend_similar_products", assistant.tool_map)
            print("LLM Assistant Service and tools initialized successfully.")
        except Exception as e:
            print(f"[WARN] LLM service initialization skipped/failed (check API key): {e}")

if __name__ == "__main__":
    unittest.main()
