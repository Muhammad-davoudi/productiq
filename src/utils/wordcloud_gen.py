from collections import Counter
import re
import arabic_reshaper
from bidi.algorithm import get_display

STOPWORDS = {"از", "به", "که", "و", "در", "این", "با", "برای", "است", "کرد", "کردن", "بود", "شد", "اما", "یا", "یک", "های"}

def shape_text(text):
    return get_display(arabic_reshaper.reshape(text))

def get_word_frequencies(text_data: list[str]) -> list[dict]:
    all_text = " ".join(text_data)
    words = re.findall(r'\w+', all_text)
    
    filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    counts = Counter(filtered_words)
    
    # خروجی نهایی با متن شکل‌دهی شده
    return [{"text": shape_text(word), "value": count} for word, count in counts.most_common(50)]
