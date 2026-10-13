# -*- coding: utf-8 -*-
import re
import hazm
import unicodedata

class PersianTextCleaner:
    def __init__(self):
        self.normalizer = hazm.Normalizer()
        self.stopwords = set(hazm.stopwords_list())
        # کلمات کلیدی که نقش احساسی دارند نباید حذف شوند
        self.keep_list = {"اما", "ولی", "اگرچه", "فقط", "تاحدی", "نه", "خیر", "بله", "نیست", "هست"}
        self.stopwords = self.stopwords - self.keep_list

    def clean(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""

        text = unicodedata.normalize('NFKC', text)
        text = self.normalizer.normalize(text)
        
        # حذف تگ و لینک
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        
        # حذف کشیدگی‌ها
        text = re.sub(r'(.)\1{2,}', r'\1', text)
        
        # توکنایز ساده (بدون ریشه‌یابی)
        tokens = hazm.word_tokenize(text)
        cleaned = [w for w in tokens if w not in self.stopwords and len(w) > 1]
        
        return " ".join(cleaned)
