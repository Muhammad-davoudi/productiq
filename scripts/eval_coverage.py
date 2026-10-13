import pandas as pd
import numpy as np
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.recommendation.recommender import ContentRecommender

def evaluate_coverage():
    print("\n--- Evaluating Recommendation Coverage (Fixed) ---")
    
    # Load feature matrix
    df = pd.read_csv('data/processed/product_feature_matrix.csv')
    
    # Check if 'product_id' column exists, otherwise use first column
    if 'product_id' in df.columns:
        product_ids = df['product_id'].values
    else:
        product_ids = df.iloc[:, 0].values 
        
    embeddings = df.select_dtypes(include=[np.number]).values

    # Initialize Recommender
    recommender = ContentRecommender(embeddings, product_ids)
    
    # Sample products to test
    sample_size = min(500, len(product_ids))
    sample_indices = np.random.choice(len(product_ids), sample_size, replace=False)
        
    recommended_set = set()
    total_catalog = set(product_ids)
    
    print(f"Sampling {sample_size} products to estimate coverage...")
    
    for idx in sample_indices:
        # Get top-5 recommendations using top_k
        results = recommender.get_recommendations(product_id=product_ids[idx], top_k=5)
        
        # Extract product IDs from results (assuming list of dicts)
        for res in results:
            if isinstance(res, dict) and 'product_id' in res:
                recommended_set.add(res['product_id'])
            else:
                recommended_set.add(res)
    
    coverage = (len(recommended_set) / len(total_catalog)) * 100
    
    print(f"\nResults:")
    print(f"Total Unique Products in Catalog: {len(total_catalog)}")
    print(f"Unique Products Recommended (in sample): {len(recommended_set)}")
    print(f"Estimated Catalog Coverage: {coverage:.2f}%")

if __name__ == "__main__":
    evaluate_coverage()
