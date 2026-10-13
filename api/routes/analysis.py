from fastapi import APIRouter, HTTPException
from src.database.connection import get_db
from sqlalchemy.orm import Session
from src.utils.wordcloud_gen import get_word_frequencies
from fastapi import Depends

router = APIRouter(prefix="/api/reviews", tags=["analysis"])

@router.get("/wordcloud/{product_id}")
def get_wordcloud_data(product_id: int, db: Session = Depends(get_db)):
    # در اینجا فرض بر این است که متون از جدول review_sentences خوانده می‌شوند
    # شما می‌توانید کوئری را بر اساس نیاز تغییر دهید
    reviews = db.execute(
        "SELECT sentence FROM review_sentences WHERE product_id = :pid", 
        {"pid": product_id}
    ).fetchall()
    
    if not reviews:
        return {"data": [], "stats": {"all": 0, "positive": 0, "negative": 0, "neutral": 0}}
        
    texts = [r[0] for r in reviews]
    word_data = get_word_frequencies(texts)
    
    # در صورت نیاز به آمار برای دکمه‌های بالا:
    # (اینجا فعلاً مقادیر فرضی است تا ساختار دستت بیاید)
    stats = {"all": len(texts), "positive": len(texts)//2, "negative": len(texts)//4, "neutral": len(texts)//4}
    
    return {"data": word_data, "stats": stats}
