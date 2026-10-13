import re
import numpy as np

class ReviewAggregator:
    def __init__(self):
        # بازه خنثی گسترش یافته برای جلوگیری از برچسب‌های منفیِ کاذب
        self.safe_zone = 0.3

    def split_sentences(self, text):
        # تقسیم متن به جملات بر اساس علائم نگارشی
        sentences = re.split(r'[.!?،\n]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 3]

    def aggregate(self, sentences, sentence_probs):
        """
        sentence_probs: لیست احتمالاتِ مدل (3 کلاس: Neg, Neu, Pos)
        """
        if not sentences:
            return "Uncertain"

        # ایندکس 0: منفی، 1: خنثی، 2: مثبت
        scores = []
        for prob in sentence_probs:
            # امتیاز: احتمال مثبت منهای احتمال منفی (محدوده بین 1- تا 1+)
            score = prob[2] - prob[0]
            scores.append(score)

        # وزن‌دهی: جمله آخر ضریب 1.5
        weights = [1.0] * len(scores)
        weights[-1] = 1.5
        
        # محاسبه میانگین وزن‌دار
        weighted_avg = np.average(scores, weights=weights)
        
        # تشخیص Conflict: واریانس بالا (تضاد شدید)
        if len(scores) > 1 and max(scores) > 0.5 and min(scores) < -0.5:
            return "Conflicted"

        # طبقه‌بندی ۷‌گانه با بازه‌های جدید
        if weighted_avg > 0.6: return "Positive"
        if weighted_avg > 0.3: return "Mostly Positive"
        if -self.safe_zone <= weighted_avg <= self.safe_zone: return "Neutral"
        if weighted_avg > -0.6: return "Mostly Negative"
        return "Negative"
