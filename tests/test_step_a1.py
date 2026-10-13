import sys
from src.recommendation.recommender import ContentRecommender

def run_tests():
    recommender = ContentRecommender()
    test_title = "گوشی موبایل سامسونگ"

    print("Running Test 1: Deterministic output check...")
    res1 = recommender.get_similar_products_by_title(test_title, limit=5)
    res2 = recommender.get_similar_products_by_title(test_title, limit=5)

    assert len(res1) <= 5, "Exceeded limit of 5 items"
    assert [r['id'] for r in res1] == [r['id'] for r in res2], "Ranking is not deterministic!"
    print(f"Test 1 Passed: Retrieved {len(res1)} deterministic items.")

    print("\nRunning Test 2: Source product exclusion...")
    if res1:
        first_title = res1[0]['title']
        sub_recs = recommender.get_similar_products_by_title(first_title, limit=5)
        for r in sub_recs:
            assert r['title'] != first_title, f"Source product {first_title} returned in its own recommendations!"
        print("Test 2 Passed: Source product excluded properly.")

    print("\nRunning Test 3: Invalid and empty inputs...")
    assert recommender.get_similar_products_by_title("") == []
    assert recommender.get_similar_products_by_title("   ") == []
    print("Test 3 Passed: Handled empty/invalid input safely.")

    print("\nSample Recommendations:")
    for idx, item in enumerate(res1, 1):
        print(f"{idx}. {item['title']} - {item['price']}")

    print("\nALL STEP A1 TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
