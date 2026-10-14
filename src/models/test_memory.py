import os
import sys

print("Phase 1: Starting test...", flush=True)

# 1. تست بارگذاری کتابخانه‌ها (سنگین‌ترین بخش)
print("Phase 2: Importing UnifiedFeatureExtractor...", flush=True)
try:
    from src.nlp.feature_engineering import UnifiedFeatureExtractor
    print("Success: Feature extractor imported.", flush=True)
except Exception as e:
    print(f"CRASH in import: {e}", flush=True)
    sys.exit(1)

# 2. تست نمونه‌سازی (بارگذاری مدل در رم)
print("Phase 3: Initializing model (Loading weights into RAM)...", flush=True)
try:
    extractor = UnifiedFeatureExtractor()
    print("Success: Model initialized in RAM.", flush=True)
except Exception as e:
    print(f"CRASH in initialization: {e}", flush=True)
    sys.exit(1)

print("Test complete. No memory crash.", flush=True)
