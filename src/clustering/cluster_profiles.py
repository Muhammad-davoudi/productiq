import pandas as pd
import numpy as np

def get_cluster_name(cluster_id):
    # Mapping for 7 clusters (0-6)
    mapping = {
        0: "General_Purpose",
        1: "Premium_Segment",
        2: "Niche_Luxury",
        3: "Budget_Friendly",
        4: "High_End_Tech",
        5: "Specialized_Accessory",
        6: "Seasonal_Promotional"
    }
    return mapping.get(cluster_id, "Unknown_Segment")

def compute_profiles(cluster_df):
    """
    Computes profile stats for each cluster dynamically.
    """
    print("Computing profiles for 7 clusters...")
    profiles = cluster_df.groupby('cluster').agg({
        'price': 'mean',
        'rate': 'mean',
        'rate_cnt': 'mean'
    }).reset_index()
    
    profiles['cluster_name'] = profiles['cluster'].apply(get_cluster_name)
    return profiles

if __name__ == "__main__":
    df = pd.read_csv('data/processed/product_clusters.csv')
    profiles = compute_profiles(df)
    print(profiles)
