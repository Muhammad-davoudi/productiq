import re
from typing import List, Dict

# Standard normalized domain ontology for e-commerce reviews
ASPECT_TAXONOMY = {
    "کیفیت": ["کیفیت", "کیفیتش", "جنس", "متریال", "ساخت", "مرغوب"],
    "قیمت": ["قیمت", "قیمتش", "ارزش خرید", "ارزش", "گرون", "گران", "ارزان", "مقرون‌به‌صرفه"],
    "باتری": ["باتری", "باطری", "شارژ", "شارژدهی", "نگهداری شارژ"],
    "دوربین": ["دوربین", "دوربینش", "لنز", "عکسبرداری", "فیلمبرداری"],
    "طراحی": ["طراحی", "ظاهر", "خوش‌دست", "شکل", "رنگ", "زیبایی"],
    "بسته‌بندی": ["بسته‌بندی", "جعبه", "پلمپ", "کارتن"],
    "ارسال": ["ارسال", "تحویل", "پیک", "پست", "تاخیر", "به‌موقع"],
    "عملکرد": ["سرعت", "هنگ", "قدرت", "عملکرد", "پردازنده", "تاچ"]
}

class AspectExtractor:
    """Extract and normalize candidate product aspects from Persian sentences."""
    def __init__(self, taxonomy: Dict[str, List[str]] = None):
        self.taxonomy = taxonomy or ASPECT_TAXONOMY
        self._lookup = {}
        for canonical, variants in self.taxonomy.items():
            for v in variants:
                self._lookup[v] = canonical

    def extract_aspects(self, sentence: str) -> List[str]:
        if not sentence or not isinstance(sentence, str):
            return []
        
        found = set()
        clean_text = sentence.strip()
        
        for variant, canonical in self._lookup.items():
            pattern = rf"(^|[^\w\u0600-\u06FF]){re.escape(variant)}([^\w\u0600-\u06FF]|$)"
            if re.search(pattern, clean_text):
                found.add(canonical)
                
        return sorted(list(found))
