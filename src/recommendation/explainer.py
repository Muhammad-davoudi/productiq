import pandas as pd
import numpy as np
import os

class RecommenderExplainer:
    def __init__(self, feature_path="data/processed/product_feature_matrix.csv", 
                 cluster_path="data/processed/product_clusters.csv"):
        self.df = pd.read_csv(feature_path)
        self.clusters = pd.read_csv(cluster_path)
        self.df = self.df.merge(self.clusters, on='product_id', how='left')
        self.df = self.df.set_index('product_id')

    def get_features(self, product_id):
        if product_id not in self.df.index:
            return None
        return self.df.loc[product_id]

    def explain(self, source_id, target_id, similarity_score):
        src = self.get_features(source_id)
        tgt = self.get_features(target_id)
        
        if src is None or tgt is None:
            return ["اطلاعات کافی برای توضیح موجود نیست."]

        reasons = []
        
        # 1. Similarity Logic (Deterministic)
        if similarity_score > 0.7:
            reasons.append("شباهت محتوایی بسیار بالا")
        elif similarity_score > 0.5:
            reasons.append("شباهت محتوایی مناسب")

        # 2. Category Logic
        if src.get('category') == tgt.get('category'):
            if src.get('subcategory') == tgt.get('subcategory'):
                reasons.append("هم‌دسته‌بندی و هم‌زیر‌دسته")
            else:
                reasons.append("هم‌دسته‌بندی")

        # 3. Price Logic
        price_diff = abs(src.get('price', 0) - tgt.get('price', 0)) / (src.get('price', 1) + 1e-9)
        if price_diff < 0.2:
            reasons.append("بازه قیمتی مشابه")
        elif tgt.get('price', 0) < src.get('price', 0):
            reasons.append("قیمت پایین‌تر")

        # 4. Rating & Sentiment
        if tgt.get('rate', 0) > src.get('rate', 0) + 0.5:
            reasons.append("امتیاز کاربران بالاتر")
        
        if tgt.get('recommendation_ratio', 0) > src.get('recommendation_ratio', 0) + 0.1:
            reasons.append("رضایت مشتریان بیشتر")

        # 5. Cluster Logic
        if 'cluster' in src and 'cluster' in tgt and src['cluster'] == tgt['cluster']:
            reasons.append("در یک دسته محصولی (Cluster) مشابه")

        return reasons if reasons else ["توصیه شده بر اساس الگوریتم شباهت محتوایی"]
