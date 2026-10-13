import os
import pandas as pd
from typing import Dict, Any

class AnalyticsService:
    @staticmethod
    def get_dashboard_data() -> Dict[str, Any]:
        prods_path = "data/processed/cleaned_products.csv"
        comms_path = "data/processed/cleaned_comments.csv"

        if not os.path.exists(prods_path) or not os.path.exists(comms_path):
            # Fallback to raw if not yet processed
            prods_path = "data/raw/digikala-products.csv"
            comms_path = "data/raw/digikala-comments.csv"

        df_prods = pd.read_csv(prods_path, encoding="utf-8-sig")
        df_comms = pd.read_csv(comms_path, encoding="utf-8-sig")

        # 1. KPI
        kpi = {
            "total_products": int(len(df_prods)),
            "total_reviews": int(len(df_comms)),
            "average_rating": round(float(df_prods["Rate"].mean()), 2) if "Rate" in df_prods else 0.0,
            "number_of_categories": int(df_prods["Category1"].nunique()) if "Category1" in df_prods else 0
        }

        # 2. Charts Data
        cat_counts = df_prods["Category1"].value_counts().head(10).reset_index()
        cat_counts.columns = ["label", "value"]

        brand_counts = df_prods["Brand"].value_counts().head(10).reset_index()
        brand_counts.columns = ["label", "value"]

        rec_counts = df_comms["recommendation_status"].value_counts().reset_index()
        rec_counts.columns = ["label", "value"]

        buyer_counts = df_comms["is_buyer"].value_counts().reset_index()
        buyer_counts.columns = ["label", "value"]
        buyer_counts["label"] = buyer_counts["label"].apply(lambda x: "خریدار" if bool(x) else "غیرخریدار")

        # Sample for scatter chart to keep payload light and fast
        scatter_sample = df_prods[["Price", "Rate", "title_fa"]].dropna().sample(min(len(df_prods), 500), random_state=42)
        price_vs_rating = scatter_sample.to_dict(orient="records")

        # 3. Dynamic Insights
        top_cat = cat_counts.iloc[0]["label"] if not cat_counts.empty else "نامشخص"
        top_cat_pct = round((cat_counts.iloc[0]["value"] / len(df_prods)) * 100, 1) if not cat_counts.empty else 0
        
        median_price = df_prods["Price"].median() if "Price" in df_prods else 0
        buyer_pct = round((df_comms["is_buyer"].sum() / len(df_comms)) * 100, 1) if len(df_comms) > 0 and "is_buyer" in df_comms else 0

        insights = [
            {
                "title": "دسته‌بندی پیشتاز",
                "detail": f"بیشترین سهم تنوع محصول متعلق به دسته «{top_cat}» با {top_cat_pct}% از کل محصولات است."
            },
            {
                "title": "میانه قیمتی بازار",
                "detail": f"میانه قیمت محصولات در کاتالوگ {median_price:,.0f} ریال می‌باشد."
            },
            {
                "title": "مشارکت خریداران قطعی",
                "detail": f"{buyer_pct}% از ثبت‌کنندگان نظرات، خریداران تایید‌شده همان کالا بوده‌اند."
            }
        ]

        return {
            "kpi": kpi,
            "products_by_category": cat_counts.to_dict(orient="records"),
            "products_by_brand": brand_counts.to_dict(orient="records"),
            "price_distribution": df_prods["Price"].clip(upper=df_prods["Price"].quantile(0.95)).dropna().tolist(),
            "rating_distribution": df_prods["Rate"].dropna().tolist(),
            "review_rating_distribution": df_comms["rate"].dropna().tolist() if "rate" in df_comms else [],
            "recommendation_status": rec_counts.to_dict(orient="records"),
            "buyer_status": buyer_counts.to_dict(orient="records"),
            "price_vs_rating": price_vs_rating,
            "insights": insights
        }
