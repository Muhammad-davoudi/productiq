import sys
from src.llm.service import AssistantService
from src.llm.adapter import (
    search_products,
    get_categories,
    search_by_price,
    search_exact,
    recommend_similar_products
)

def run_regression_checks():
    print("--- 1. Testing Tool Registry Integrity ---")
    service = AssistantService()
    expected_order = [
        "search_products",
        "get_categories",
        "search_by_price",
        "search_exact",
        "recommend_similar_products"
    ]
    registered_names = [t.name for t in service.tools]
    print(f"Registered tools: {registered_names}")
    assert registered_names == expected_order, f"Tool order mismatch! Expected: {expected_order}, got: {registered_names}"
    print("Check 1 Passed: 4 original tools preserved in order, new tool added as 5th.")

    print("\n--- 2. Testing Direct Execution of Original 4 Tools ---")
    p_res = search_products.invoke({"query": "سامسونگ"})
    assert isinstance(p_res, list) and len(p_res) <= 5
    print(f"search_products passed (returned {len(p_res)} items)")

    c_res = get_categories.invoke({})
    assert isinstance(c_res, list) and len(c_res) <= 5
    print(f"get_categories passed (returned {len(c_res)} categories)")

    pr_res = search_by_price.invoke({"max_price": 500000})
    assert isinstance(pr_res, list) and len(pr_res) <= 5
    print(f"search_by_price passed (returned {len(pr_res)} items)")

    ex_res = search_exact.invoke({"product_name": "نامعتبر_وجود_ندارد"})
    assert isinstance(ex_res, list) and len(ex_res) == 0
    print("search_exact passed")

    print("\n--- 3. Testing Direct Execution of New Recommendation Tool ---")
    rec_res = recommend_similar_products.invoke({"product_title": "گوشی موبایل سامسونگ"})
    assert isinstance(rec_res, list) and len(rec_res) <= 5
    print(f"recommend_similar_products passed (returned {len(rec_res)} items)")

    empty_rec = recommend_similar_products.invoke({"product_title": ""})
    assert empty_rec == "هیچ کالای مشابهی یافت نشد."
    print("recommend_similar_products empty input handling passed")

    print("\n--- 4. Testing End-to-End LLM Service Execution ---")
    reply = service.process_input("test_session_id", "یک کالای مشابه گوشی سامسونگ پیشنهاد بده")
    print(f"LLM Reply:\n{reply}\n")
    assert "*" not in reply, "Markdown asterisks (*) found in response!"
    print("Check 4 Passed: Response received with zero asterisks.")

    print("\nALL PHASE A REGRESSION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_regression_checks()
