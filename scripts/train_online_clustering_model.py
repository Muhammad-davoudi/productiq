import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
import os

SOURCE_CSV = "data/processed/product_clusters_two_stage.csv"
MODEL_PATH = "models/online_cluster_classifier.joblib"

print(f"Reading training data from {SOURCE_CSV}...")
df = pd.read_csv(SOURCE_CSV, usecols=['price', 'rate', 'rate_cnt', 'cluster'])
df = df.dropna(subset=['cluster'])

# استخراج ویژگی‌های قابل دستیابی در پیام کافکا
X = df[['price', 'rate', 'rate_cnt']].fillna(0).values
y = df['cluster'].astype(int).values

print(f"Dataset shape: {X.shape}, unique clusters: {np.unique(y)}")
print("Training lightweight online classifier to predict the 6 clusters...")

clf = HistGradientBoostingClassifier(max_iter=50, random_state=42)
clf.fit(X, y)

os.makedirs("models", exist_ok=True)
joblib.dump(clf, MODEL_PATH)
print(f"Model successfully saved to {MODEL_PATH}")
