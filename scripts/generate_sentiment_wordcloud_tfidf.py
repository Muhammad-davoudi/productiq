#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

FA_STOPWORDS = {
    "و", "در", "به", "از", "که", "این", "آن", "با", "برای", "را", "رو", "تا", "اما", "یا", "اگر", "پس",
    "هم", "هیچ", "من", "تو", "او", "ما", "شما", "ایشان", "های", "هایی", "ترین", "تر", "یک", "دو", "سه",
    "چه", "همه", "است", "بود", "شد", "می", "می‌", "نمی", "نمی‌", "هست", "هستم", "هستی", "هستیم", "هستید",
    "هستند", "کرد", "کردم", "کردی", "کرده", "کردیم", "کردید", "کردند", "شود", "شده", "دارم", "داری",
    "دارد", "داریم", "دارید", "دارند", "ندارم", "نداری", "ندارد", "خیلی", "بسیار", "واقعا", "واقعاً",
    "اصلا", "اصلاً", "همیشه", "تقریبا", "بیشتر", "کمتر", "فقط", "حتی", "دیگه", "دیگر", "همین", "اون",
    "اینجا", "اونجا", "خود", "چون", "ولی", "باشه", "باشند", "باید", "نباید", "چند", "همچنان", "قبل",
    "بعد", "زیر", "روی", "بین", "بدون", "پیش", "کنید", "کنم", "کنه", "کنند", "کنی", "لطفا", "لطفاً"
}

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace("\u200c", " ").replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"[^آ-یA-Za-z0-9\s]", " ", text)
    tokens = [t.strip().lower() for t in text.split() if len(t.strip()) > 1 and not t.strip().isdigit()]
    tokens = [t for t in tokens if t not in FA_STOPWORDS]
    return " ".join(tokens)

def extract_top_tfidf(corpus, top_n=30):
    if not corpus or len(corpus) < 2:
        return []
    
    vec = TfidfVectorizer(max_features=2000, token_pattern=r"(?u)\b\w+\b")
    try:
        X = vec.fit_transform(corpus)
    except ValueError:
        return []

    feature_names = np.array(vec.get_feature_names_out())
    # مجموع وزن‌های TF-IDF برای هر واژه در دسته
    tfidf_scores = np.asarray(X.sum(axis=0)).ravel()
    
    # شمارش تعداد تکرار خام برای نمایش در داشبورد
    binary_counts = np.asarray((X > 0).sum(axis=0)).ravel()

    sorted_indices = tfidf_scores.argsort()[::-1]
    
    results = []
    for idx in sorted_indices:
        word = feature_names[idx]
        if word in FA_STOPWORDS or len(word) < 2:
            continue
        results.append({
            "word": word,
            "count": int(binary_counts[idx]),
            "tfidf_score": round(float(tfidf_scores[idx]), 3)
        })
        if len(results) >= top_n:
            break
            
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="labeling_sample_1200.csv", help="مسیر فایل ورودی")
    parser.add_argument("--out", default="data/sentiment_wordcloud_top30.json", help="مسیر فایل خروجی")
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()

    # در صورت نبودن فایل در مسیر فعلی، بررسی پوشه‌های رایج
    input_path = args.input
    if not os.path.exists(input_path):
        for candidate in [os.path.join("data", args.input), os.path.join("notebooks", args.input)]:
            if os.path.exists(candidate):
                input_path = candidate
                break

    df = pd.read_csv(input_path)
    
    text_col = "text" if "text" in df.columns else ("sentence_text" if "sentence_text" in df.columns else None)
    if not text_col:
        raise ValueError("ستون متن (text یا sentence_text) در فایل یافت نشد.")

    # تعیین دسته بر اساس label یا rate
    if "label" in df.columns:
        df["category"] = df["label"].astype(str).str.lower().str.strip()
    elif "rate" in df.columns:
        def rate_to_sentiment(r):
            try:
                val = float(r)
                if val >= 4.0: return "positive"
                if val <= 2.0: return "negative"
                return "neutral"
            except:
                return "neutral"
        df["category"] = df["rate"].apply(rate_to_sentiment)
    else:
        df["category"] = "all"

    # پاک‌سازی و حذف Stopword
    df["cleaned_text"] = df[text_col].apply(clean_text)

    categories = df["category"].unique()
    output_data = {
        "metadata": {
            "source_file": input_path,
            "total_rows": len(df),
            "top_words_limit": args.top,
            "method": "TF-IDF + Frequency"
        },
        "wordcloud_by_sentiment": {}
    }

    for cat in categories:
        sub_corpus = df[df["category"] == cat]["cleaned_text"].dropna().tolist()
        sub_corpus = [c for c in sub_corpus if len(c.strip()) > 0]
        output_data["wordcloud_by_sentiment"][str(cat)] = extract_top_tfidf(sub_corpus, top_n=args.top)

    # کل نظرات تجمیعی (کلی)
    all_corpus = df["cleaned_text"].dropna().tolist()
    output_data["wordcloud_by_sentiment"]["overall"] = extract_top_tfidf(all_corpus, top_n=args.top)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ فایل با موفقیت تولید شد: {args.out}")
    for cat, words in output_data["wordcloud_by_sentiment"].items():
        print(f" - دسته '{cat}': {len(words)} کلمه استخراج شد.")

if __name__ == "__main__":
    main()
