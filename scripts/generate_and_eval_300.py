import pandas as pd
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models.predict import analyze_review

# Paths
comments_path = 'data/raw/digikala-comments.csv'
processed_data_path = 'data/processed/labeling_sample_1200_labeled.csv'
output_path = 'data/processed/eval_set_300_predicted.csv'

print("Loading data for unseen evaluation...")
df_raw = pd.read_csv(comments_path)
df_used = pd.read_csv(processed_data_path)

# Filter: Use 'body' for text and exclude IDs used in the 1200-set
used_ids = df_used['id'].unique() if 'id' in df_used.columns else []
df_unused = df_raw[~df_raw['id'].isin(used_ids)].copy()

# Drop rows where 'body' is empty/NaN
df_unused = df_unused.dropna(subset=['body'])

# Sample 300 unseen rows
eval_df = df_unused.sample(n=300, random_state=42).copy()

print("Running BERT model inference on 300 unseen samples...")
predictions = []
for text in eval_df['body']:
    try:
        # Use str() to ensure it's text
        res = analyze_review(str(text))
        predictions.append(res['final'] if isinstance(res, dict) else res)
    except Exception as e:
        predictions.append("Error")

eval_df['predicted_sentiment'] = predictions
eval_df.to_csv(output_path, index=False)

print(f"\nSuccessfully saved predictions to {output_path}")
print("\n--- Predicted Sentiment Distribution on 300 Unseen Samples ---")
print(eval_df['predicted_sentiment'].value_counts())
