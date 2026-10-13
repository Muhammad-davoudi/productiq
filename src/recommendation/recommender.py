import os
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

load_dotenv(find_dotenv())

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)

STOP_WORDS = {
    'و', 'در', 'به', 'از', 'که', 'این', 'رو', 'با', 'برای', 'آن', 'یک', 'تا',
    'بر', 'یا', 'هم', 'نیز', 'اما', 'می', 'شد', 'مدل', 'کد', 'سایز'
}

def clean_and_tokenize(text_val: str) -> List[str]:
    if not text_val:
        return []
    cleaned = re.sub(r'[^\w\s]', ' ', text_val)
    tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
    return [t for t in tokens if t not in STOP_WORDS]

class ContentRecommender:
    def __init__(self):
        self.engine = engine

    def get_similar_products_by_title(self, product_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        یافتن قطعی و دیتابیسی محصولات مشابه بر اساس دسته‌بندی مشترک و هم‌پوشانی عنوان
        کاملاً بدون رندوم و با خروجی پایدار
        """
        if not product_title or not product_title.strip():
            return []

        search_term = product_title.strip()
        tokens = clean_and_tokenize(search_term)

        with self.engine.connect() as conn:
            # 1. یافتن دقیق‌ترین محصول منبع در دیتابیس
            source_query = text("""
                SELECT id, title_fa, category1, price
                FROM products_curated
                WHERE title_fa ILIKE :title
                ORDER BY id ASC
                LIMIT 1
            """)
            source_res = conn.execute(source_query, {"title": f"%{search_term}%"}).fetchone()

            source_id = None
            category = None
            source_price = None

            if source_res:
                source_id = source_res[0]
                category = source_res[2]
                source_price = source_res[3]
                if not tokens:
                    tokens = clean_and_tokenize(source_res[1])

            # اگر هیچ توکنی استخراج نشد
            if not tokens:
                return []

            # 2. جستجوی کاندیداها بر اساس توکن‌های عنوان و دسته مشترک
            # اولویت اول: هم‌دسته‌ای و اشتراک کلمات کلیدی، به دور از خود محصول
            conditions = []
            params: Dict[str, Any] = {"limit": limit}

            if source_id is not None:
                conditions.append("id != :source_id")
                params["source_id"] = source_id

            token_clauses = []
            for idx, token in enumerate(tokens[:4]):
                p_name = f"tok_{idx}"
                token_clauses.append(f"title_fa ILIKE :{p_name}")
                params[p_name] = f"%{token}%"

            if token_clauses:
                conditions.append(f"({' OR '.join(token_clauses)})")

            if category:
                conditions.append("category1 = :category")
                params["category"] = category

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            query_sql = f"""
                SELECT id, title_fa, category1, price
                FROM products_curated
                WHERE {where_clause}
                ORDER BY id ASC
                LIMIT :limit
            """

            candidates = conn.execute(text(query_sql), params).fetchall()

            # 3. در صورتی که با دسته مشترک چیزی پیدا نشد، بدون قید دسته جستجو کن
            if not candidates and category:
                conditions_fallback = []
                params_fallback: Dict[str, Any] = {"limit": limit}
                if source_id is not None:
                    conditions_fallback.append("id != :source_id")
                    params_fallback["source_id"] = source_id

                token_clauses_fb = []
                for idx, token in enumerate(tokens[:3]):
                    p_name = f"fb_tok_{idx}"
                    token_clauses_fb.append(f"title_fa ILIKE :{p_name}")
                    params_fallback[p_name] = f"%{token}%"

                if token_clauses_fb:
                    conditions_fallback.append(f"({' OR '.join(token_clauses_fb)})")

                where_fb = " AND ".join(conditions_fallback) if conditions_fallback else "1=1"
                fallback_sql = f"""
                    SELECT id, title_fa, category1, price
                    FROM products_curated
                    WHERE {where_fb}
                    ORDER BY id ASC
                    LIMIT :limit
                """
                candidates = conn.execute(text(fallback_sql), params_fallback).fetchall()

            results = []
            for row in candidates:
                price_val = row[3]
                price_str = f"{price_val:,.0f} تومان" if price_val is not None else "نامشخص"
                results.append({
                    "id": row[0],
                    "title": row[1],
                    "category": row[2] or "",
                    "price": price_str
                })

            return results
