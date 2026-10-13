import pandas as pd
import os

# Paths
raw_data_path = 'data/raw/digikala-products.csv' # Assuming this is the raw file
processed_data_path = 'data/processed/labeling_sample_1200_labeled.csv'
output_path = 'data/processed/eval_set_300.csv'

# Load files
df_raw = pd.read_csv(raw_data_path)
df_used = pd.read_csv(processed_data_path)

# Exclude already used IDs to ensure "Unseen" data
used_ids = df_used['id'].unique()
df_unused = df_raw[~df_raw['id'].isin(used_ids)]

# Sample 300
eval_set = df_unused.sample(n=300, random_state=42)

# Save
eval_set.to_csv(output_path, index=False)
print(f"Successfully created {output_path} with {len(eval_set)} samples.")
