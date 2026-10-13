import json
import os

class ContentRecommender:
    def __init__(self):
        self.data_path = "data/recommendations.json"
        self.recommendations = self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_similar_products(self, product_id):
        """بازگرداندن پیشنهادات از فایل پیش‌محاسبه شده"""
        pid_str = str(product_id)
        # بازگشت لیست پیشنهادی یا یک لیست خالی اگر چیزی پیدا نشد
        return self.recommendations.get(pid_str, [])
