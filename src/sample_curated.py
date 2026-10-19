import os
import pandas as pd
from sqlalchemy import create_engine, text

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgrespassword")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "digikala_db")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def run_sampling():
    print("Reading clean products from database...")
    query = """
        SELECT * FROM products
        WHERE category1 IS NOT NULL
          AND TRIM(category1) != ''
          AND category1 NOT ILIKE '%nan%'
          AND category1 NOT ILIKE '%نامشخص%'
          AND price > 0;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    print(f"Total clean products found: {len(df)}")

    cat_counts = df['category1'].value_counts()
    small_cats = [cat for cat, count in cat_counts.items() if count < 100]
    large_cats = [cat for cat, count in cat_counts.items() if count >= 100]

    sampled_dfs = []
    target_total = 1500

    for cat in small_cats:
        group = df[df['category1'] == cat]
        sample_size = min(len(group), 2)
        sampled_dfs.append(group.sample(n=sample_size, random_state=42))

    current_count = sum(len(d) for d in sampled_dfs)
    remaining_needed = max(0, target_total - current_count)

    if large_cats and remaining_needed > 0:
        large_df = df[df['category1'].isin(large_cats)]
        if len(large_df) <= remaining_needed:
            sampled_dfs.append(large_df)
        else:
            sampled_large = large_df.sample(n=remaining_needed, random_state=42)
            sampled_dfs.append(sampled_large)

    final_df = pd.concat(sampled_dfs, ignore_index=True)

    if len(final_df) > target_total:
        final_df = final_df.sample(n=target_total, random_state=42)

    print(f"Final sampled dataset size: {len(final_df)}")

    print("Writing sampled data to `products_curated` table...")
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE products_curated CASCADE;"))
        final_df.to_sql('products_curated', con=connection, if_exists='append', index=False)

    print("Sampling and insertion into `products_curated` completed successfully!")

if __name__ == "__main__":
    run_sampling()
