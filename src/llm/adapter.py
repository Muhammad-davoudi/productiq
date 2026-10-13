import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text
from langchain_core.tools import tool

# بارگذاری تنظیمات
load_dotenv(find_dotenv())

# ساخت URL اتصال از اجزای موجود در .env
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_password, db_name]):
    raise ValueError("اطلاعات اتصال دیتابیس در فایل .env یافت نشد.")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)

@tool
def search_products(query: str):
    """Search for products by title."""
    # لیست کلمات ممنوعه را اینجا مدیریت کنید
    excluded_keywords = [
        'بازی', 'آموزشی', 'کتاب', 'کفش', 'لوازم آرایشی', 
        'کوله', 'لوازم منزل', 'لوازم کودک', 'کفش ورزشی', 
        'کفش زنانه مجلسی'
    ]
    
    # ساخت بخش فیلتر به صورت پویا
    filter_sql = ""
    params = {"query": f"%{query}%"}
    
    for i, kw in enumerate(excluded_keywords):
        param_name = f"ex_{i}"
        filter_sql += f" AND title_fa NOT ILIKE :{param_name}"
        params[param_name] = f"%{kw}%"
        
    sql = text(f"""
        SELECT title_fa, price FROM products_curated 
        WHERE title_fa ILIKE :query 
        {filter_sql}
        LIMIT 5
    """)
    
    with engine.connect() as conn:
        result = conn.execute(sql, params)
        products = result.fetchall()
        return [{"title": p[0], "price": f"{p[1]:,.0f} تومان"} for p in products]

@tool
def get_categories():
    """List available product categories."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT category1 FROM products_curated LIMIT 5"))
        return [row[0] for row in result.fetchall()]

@tool
def search_by_price(max_price: int):
    """Filter products by maximum price."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT title_fa, price FROM products_curated WHERE price <= :max_price LIMIT 5"),
            {"max_price": max_price}
        )
        products = result.fetchall()
        return [{"title": p[0], "price": f"{p[1]:,.0f} تومان"} for p in products]

@tool
def search_exact(product_name: str):
    """Search for an exact product name."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT title_fa, price FROM products_curated WHERE title_fa = :name LIMIT 5"),
            {"name": product_name}
        )
        products = result.fetchall()
        return [{"title": p[0], "price": f"{p[1]:,.0f} تومان"} for p in products]
