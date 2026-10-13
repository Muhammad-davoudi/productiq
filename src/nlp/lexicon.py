import re

class SentimentLexiconFeaturizer:
    def __init__(self):
        # کلمات کلیدی توسعه‌یافته بر اساس فضای نظرات دیجی‌کالا
        self.positive_words = {
            'عالی', 'خوب', 'راضی', 'بهترین', 'باکیفیت', 'عالیه', 'پیشنهاد', 'کاربردی',
            'خرید', 'ارزش', 'زیبا', 'شیک', 'سریع', 'دقیق', 'کاملا', 'مفید', 'مقرون',
            'مناسب', 'راحت', 'اصلی', 'اورجینال', 'ممنون', 'تشکر'
        }
        self.negative_words = {
            'بد', 'افتضاح', 'ناراضی', 'بدترین', 'بی‌کیفیت', 'خراب', 'پشیمان', 'ضعیف',
            'نخرید', 'گران', 'نامناسب', 'مشکل', 'شکسته', 'تقلبی', 'دیر', 'کثیف',
            'مرجوع', 'دروغ', 'هزینه', 'بی‌ارزش', 'اصلاً', 'متاسف'
        }
        # Regex برای جدا کردن کلمات و نادیده گرفتن علائم نگارشی
        self.pattern = re.compile(r'\w+')

    def get_features(self, text):
        if not text or not isinstance(text, str):
            return {'pos_score': 0, 'neg_score': 0, 'sentiment_delta': 0}
            
        # توکنایز کردن متن
        words = self.pattern.findall(text)
        total = len(words) if len(words) > 0 else 1
        
        # شمارش
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        return {
            'pos_score': pos_count / total,
            'neg_score': neg_count / total,
            'sentiment_delta': (pos_count - neg_count) / total
        }

    def transform(self, texts):
        return [self.get_features(text) for text in texts]
