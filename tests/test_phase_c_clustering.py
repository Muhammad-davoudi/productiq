import sys
import numpy as np
from unittest.mock import MagicMock
from src.kafka.clustering_consumer import (
    safe_float,
    extract_features,
    fallback_cluster_rule,
    predict_cluster,
    load_clustering_model,
)

print("=== Running Phase C - Clustering Reliability Tests ===")

# Test 1: Safe float conversion
print("Test 1: Safe Float Parsing...")
assert safe_float(12.5) == 12.5
assert safe_float("1500000") == 1500000.0
assert safe_float("invalid") == 0.0
assert safe_float(None) == 0.0
assert safe_float(np.nan) == 0.0
print("✓ Test 1 Passed: safe_float handles edge cases gracefully.")

# Test 2: Feature extraction with mixed cases and missing keys
print("Test 2: Feature Extraction...")
f1 = extract_features({"price": 500000, "rate": 4.5, "rate_cnt": 10})
assert f1 == (500000.0, 4.5, 10.0)

f2 = extract_features({"Price": "1200000", "Rate": "3.8", "Rate_cnt": "25"})
assert f2 == (1200000.0, 3.8, 25.0)

f3 = extract_features({"price": None, "rate": "invalid"})
assert f3 == (0.0, 0.0, 0.0)
print("✓ Test 2 Passed: extract_features parses variations correctly.")

# Test 3: Payload Priority 1 (Pre-assigned cluster)
print("Test 3: Payload Pre-assigned Cluster...")
assert predict_cluster({"cluster": 2, "price": 100}) == 2
assert predict_cluster({"cluster": "4", "price": 100}) == 4
print("✓ Test 3 Passed: Priority 1 pre-assigned cluster respected.")

# Test 4: Real Model Inference
print("Test 4: Real Model Inference...")
real_model = load_clustering_model()
assert real_model is not None, "Real model could not be loaded from models/online_cluster_classifier.joblib"

sample_product = {"price": 15000000.0, "rate": 4.8, "rate_cnt": 150.0}
cluster_pred = predict_cluster(sample_product, model_instance=real_model)
assert isinstance(cluster_pred, int)
assert cluster_pred in [0, 1, 2, 3, 4, 5], f"Unexpected cluster label: {cluster_pred}"
print(f"✓ Test 4 Passed: Real model inference returned valid cluster label: {cluster_pred}.")

# Test 5: Fallback behavior on model failure or missing model
print("Test 5: Fallback Behavior...")
# Active item fallback
assert fallback_cluster_rule(price=500000, rate=4.0, rate_cnt=10) == 0
# Price based inactive items fallback
assert fallback_cluster_rule(price=500000, rate=0, rate_cnt=0) == 2
assert fallback_cluster_rule(price=1500000, rate=0, rate_cnt=0) == 4
assert fallback_cluster_rule(price=4000000, rate=0, rate_cnt=0) == 3
assert fallback_cluster_rule(price=8000000, rate=0, rate_cnt=0) == 5

# Predict with failing model mock
failing_model = MagicMock()
failing_model.predict.side_effect = RuntimeError("Inference crash simulation")
fb_res = predict_cluster({"price": 500000, "rate": 0, "rate_cnt": 0}, model_instance=failing_model)
assert fb_res == 2, f"Expected fallback 2, got {fb_res}"
print("✓ Test 5 Passed: Fallback accurately activates on model error.")

print("\n=== ALL PHASE C CLUSTERING TESTS PASSED SUCCESSFULLY ===")
