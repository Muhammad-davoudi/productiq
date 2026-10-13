import sys
from unittest.mock import patch
from src.kafka.sentiment_consumer import (
    extract_review_text,
    process_sentiment_message,
)
from src.models.predict import analyze_review

print("=== Running Phase B - Step B1 Tests ===")

# Test 1: Extract Review Text Variations
print("Test 1: Extract Review Text Variations...")
assert extract_review_text({"comment": "کیفیت بسیار عالی و خوب بود"}) == "کیفیت بسیار عالی و خوب بود"
assert extract_review_text({"text": "اصلا پیشنهاد نمیکنم"}) == "اصلا پیشنهاد نمیکنم"
assert extract_review_text({"body": "معمولی بود"}) == "معمولی بود"
assert extract_review_text({}) == ""
assert extract_review_text({"comment": "   "}) == ""
print("✓ Test 1 Passed: Field extraction works as expected.")

# Test 2: Empty or Whitespace Review Handling
print("Test 2: Empty or Whitespace Handling...")
rev_id, sentiment, score = process_sentiment_message({"id": "1001", "comment": "   "})
assert rev_id == "1001"
assert sentiment == "Uncertain"
assert score is None
print("✓ Test 2 Passed: Empty review safely classified as Uncertain with score=None.")

# Test 3: Consistency between Batch (analyze_review) and Consumer
print("Test 3: Batch vs Streaming Inference Consistency...")
sample_text = "کیفیت عالی و بسته‌بندی تمیز بود، بسیار راضی هستم."
msg = {"id": "1002", "comment": sample_text}

batch_verdict = analyze_review(sample_text).get("final")
c_rev_id, c_sentiment, c_score = process_sentiment_message(msg)

assert c_rev_id == "1002"
assert c_sentiment == batch_verdict
assert c_score is None
print(f"✓ Test 3 Passed: Stream output ('{c_sentiment}') exactly matches Batch verdict ('{batch_verdict}').")

# Test 4: Controlled Inference Error Handling
print("Test 4: Controlled Inference Error Handling (No silent fallback)...")
with patch("src.kafka.sentiment_consumer.analyze_review", side_effect=RuntimeError("Model inference failed")):
    err_rev_id, err_sentiment, err_score = process_sentiment_message({"id": "1003", "comment": "تست خطا"})
    assert err_rev_id == "1003"
    assert err_sentiment == "InferenceError"
    assert err_score is None
print("✓ Test 4 Passed: Inference errors caught and mapped to InferenceError safely.")

print("\n=== ALL STEP B1 TESTS PASSED SUCCESSFULLY ===")
