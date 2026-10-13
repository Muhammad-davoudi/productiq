import re
from typing import List
from hazm import SentenceTokenizer, Normalizer

class PersianSentenceSplitter:
    """Split Persian text into clean, normalized sentences using Hazm."""
    def __init__(self):
        self.normalizer = Normalizer()
        self.tokenizer = SentenceTokenizer()

    def split(self, text: str) -> List[str]:
        if not text or not isinstance(text, str):
            return []
        
        normalized = self.normalizer.normalize(text.strip())
        sentences = self.tokenizer.tokenize(normalized)
        
        # Clean up empty fragments and punctuation-only strings
        clean_sentences = []
        for s in sentences:
            s_clean = s.strip()
            # Must have at least one Persian/alphanumeric character
            if s_clean and re.search(r"[\w\u0600-\u06FF]", s_clean):
                clean_sentences.append(s_clean)
        return clean_sentences
