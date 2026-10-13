import pandas as pd
import os

files = {
    'labeling': 'data/processed/labeling_sample_1200_labeled.csv',
    'clusters': 'data/processed/product_clusters.csv'
}

for name, path in files.items():
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=0)
        print(f"--- {name} columns ---")
        print(list(df.columns))
    else:
        print(f"--- {name} not found ---")
