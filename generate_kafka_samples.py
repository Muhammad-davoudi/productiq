import pandas as pd
import os

input_path = 'data/raw/labeling_sample_1200.csv'
output_path = 'data/raw/kafka_samples_comment_100.csv'

if not os.path.exists(input_path):
    print(f'[ERROR] Input file {input_path} not found!')
else:
    df = pd.read_csv(input_path)
    print(f'Original dataset shape: {df.shape}')
    
    if 'rate' in df.columns:
        sampled_list = []
        for rate_val, group in df.groupby('rate'):
            n_samples = min(100, len(group))
            sampled_group = group.sample(n=n_samples, random_state=42)
            sampled_list.append(sampled_group)
            print(f'Rate {rate_val}: sampled {n_samples} records.')
            
        final_df = pd.concat(sampled_list).sample(frac=1, random_state=42).reset_index(drop=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_df.to_csv(output_path, index=False)
        print(f'[SUCCESS] Created new file: {output_path} with {len(final_df)} total rows.')
    else:
        print('[ERROR] Column \'rate\' not found in dataset.')
