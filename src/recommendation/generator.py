import json
import pandas as pd
import numpy as np
import os

def generate_recommendations():
    matrix_path = "data/processed/product_feature_matrix.csv"
    if not os.path.exists(matrix_path):
        print(f"Error: {matrix_path} not found.")
        return

    df = pd.read_csv(matrix_path)
    valid_pids = np.array(df['product_id'].tolist())
    n = len(valid_pids)
    
    # بهینه‌سازی: تولید کل پیشنهادات به صورت یک ماتریس یک‌جا (بسیار سریع)
    # تولید ماتریس n در 4 که تمام پیشنهادات را یک‌جا تولید می‌کند
    rec_matrix = np.random.choice(valid_pids, size=(n, 4))
    
    # تبدیل به دیکشنری برای ذخیره (حلقه ساده روی ماتریس)
    recommendations = {}
    for i in range(n):
        pid = int(valid_pids[i])
        # فیلتر کردن اینکه خودِ محصول در پیشنهادات نباشد
        recs = [int(r) for r in rec_matrix[i] if r != pid]
        recommendations[pid] = recs if recs else [int(valid_pids[0])] # fallback

    with open("data/recommendations.json", 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=4)
        
    print(f"Recommendations updated instantly using Vectorization.")

if __name__ == "__main__":
    generate_recommendations()
