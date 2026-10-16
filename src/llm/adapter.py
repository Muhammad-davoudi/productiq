import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text
from langchain_core.tools import tool

load_dotenv(find_dotenv())

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_password, db_name]):
    raise ValueError("اطلاعات اتصال دیتابیس در فایل .env یافت نشد.")

DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)

@tool
def search_products(query: str):
    """Search for products by title or category using keyword matching or partial terms."""
    cleaned_query = query.replace("خوب", "").replace("چی داری", "").replace("کتاب", "").strip()
    if not cleaned_query or len(cleaned_query) < 2:
        cleaned_query = query

    params = {"query": f"%{query}%", "cleaned": f"%{cleaned_query}%"}

    sql = text("""
        SELECT title_fa, price FROM products_curated
        WHERE title_fa ILIKE :query OR category1 ILIKE :query OR category2 ILIKE :query
           OR title_fa ILIKE :cleaned OR category1 ILIKE :cleaned
        LIMIT 5
    """)

    with engine.connect() as conn:
        result = conn.execute(sql, params)
        products = result.fetchall()
        if not products:
            return f"متأسفانه محصولی با عنوان یا ویژگی '{query}' یافت نشد."
        return [{"title": p[0], "price": f"{p[1]:,.0f} تومان"} for p in products]

@tool
def get_categories():
    """List available product categories."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT category1 FROM products_curated WHERE category1 IS NOT NULL LIMIT 10"))
        return [row[0] for row in result.fetchall()]

@tool
def search_by_price(max_price: int, keyword: str = ""):
    """Filter products by maximum price and optional keyword (e.g. mobile, watch)."""
    if keyword:
        sql = text("""
            SELECT title_fa, price FROM products_curated
            WHERE price <= :max_price AND (title_fa ILIKE :keyword OR category1 ILIKE :keyword)
            LIMIT 5
        """)
        params = {"max_price": max_price, "keyword": f"%{keyword}%"}
    else:
        sql = text("""
            SELECT title_fa, price FROM products_curated
            WHERE price <= :max_price
            LIMIT 5
        """)
        params = {"max_price": max_price}

    with engine.connect() as conn:
        result = conn.execute(sql, params)
        products = result.fetchall()
        if not products:
            return f"هیچ محصولی با قیمت زیر {max_price:,.0f} تومان یافت نشد."
        return [{"title": p[0], "price": f"{p[1]:,.0f} تومان"} for p in products]

@tool
def search_exact(product_name: str):
    """Search for an exact product name."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT title_fa, price FROM products_curated WHERE title_fa ILIKE :name OR category1 ILIKE :name LIMIT 5"),
            {"name": f"%{product_name}%"}
        )
        products = result.fetchall()
        if not products:
            return f"محصولی با نام {product_name} پیدا نشد."
        return [{"title": p[0], "price": f"{p[1]:,.0f} تومان"} for p in products]

from src.recommendation.recommender import ContentRecommender

_recommender_instance = ContentRecommender()

@tool
def recommend_similar_products(product_title: str):
    """Recommend similar products based on a given product title or name."""
    recs = _recommender_instance.get_similar_products_by_title(product_title, limit=5)
    if not recs:
        return "هیچ کالای مشابهی یافت نشد."
    return [{"title": r["title"], "price": r["price"]} for r in recs]
