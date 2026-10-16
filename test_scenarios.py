import asyncio
from src.llm.service import AssistantService

scenarios = [
    "سلام",
    "تشکر و قدردانی",
    "خیلی ناراحتم و عصبانی هستم چرا سفارشم دیر رسید",
    "درخواست کتاب کودک دارم",
    "یک موبایل با رم ۸ گیگ معرفی کنید",
    "خیلی عصبانی‌ام، یک گوشی خوب به من پیشنهاد بده",
    "سلام خیلی خوشحالم، یک ساعت هوشمند خوب می‌خواهم",
    "کتاب داستان کودکانه معرفی کن",
    "کتاب علمی و فیزیک می‌خواهم",
    "پیشنهاد خرید کالا تا سقف 10 میلیون تومان",
    "پيشنهاد خريد كالا برای تولد دوست دخترم",
    "درخواست تبلت با ویژگی‌های مشخص و صفحه بزرگ",
    "درخواست لوازم آرایشی ایرانی باکیفیت",
    "کفش مردانه ورزشی خارجی اصل",
    "وسایل منزل و آشپزخانه",
    "اسباب بازی برای کودک ۵ ساله",
    "خداحافظ"
]

def run_tests():
    service = AssistantService()
    for i, query in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {query} ---")
        try:
            # process_input is synchronous or asynchronous? Let's call it directly or with await if async
            # Based on signature: def process_input(self, session_id, user_input)
            response = service.process_input(session_id="test-session", user_input=query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_tests()
