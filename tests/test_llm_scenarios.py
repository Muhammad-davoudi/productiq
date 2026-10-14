import sys
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.service import AssistantService

def run_llm_scenarios():
    print("\n[INIT] Initializing AssistantService for scenario testing...")
    try:
        agent = AssistantService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize AssistantService: {e}")
        return

    scenarios = [
        ("سلام", "سلام و احوالپرسی ساده"),
        ("گوشی سامسونگ معرفی کن", "درخواست جستجوی محصول"),
        ("قیمت محصولات زیر ۵۰۰ هزار تومان چقدره؟", "درخواست فیلتر بر اساس قیمت (search_by_price)"),
        ("واقعاً افتضاحه! محصولی که فرستادید کلاً خرابه و کار نمی‌کنه!", "کاربر عصبانی و گلایه‌مند"),
        ("خیلی ممنون از شما، واقعاً سرویس‌تون عالیه!", "کاربر خوشحال و تشکرکننده"),
        ("محصولی با نام ناموجودxyz123 موجود دارید؟", "درخواستی که احتمالاً نتیجه‌ای برنمی‌گرداند"),
        ("محصولی مشابه گوشی آیفون پیشنهاد بده", "درخواست پیشنهاد مشابه (recommend_similar_products)")
    ]

    print("\n=================== RUNNING LLM SCENARIOS ===================")
    for i, (prompt, desc) in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {desc} ---")
        print(f"User Input: '{prompt}'")
        try:
            # استفاده از متد process_input با پارامترهای session_id و user_input
            response = agent.process_input(session_id="test_session", user_input=prompt)
            print(f"Agent Response:\n{response}")
        except Exception as e:
            print(f"Execution Error: {e}")
        print("-" * 60)

if __name__ == "__main__":
    run_llm_scenarios()
