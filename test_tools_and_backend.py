import sys
import os
from src.llm.service import AssistantService, ALL_TOOLS

print("=== Checking LLM Tools Binding ===")
print(f"Total bound tools: {len(ALL_TOOLS)}")
for tool in ALL_TOOLS:
    print(f" - Tool Name: {tool.name}, Description: {tool.description}")

print("\n=== Initializing AssistantService ===")
try:
    service = AssistantService()
    print("AssistantService initialized successfully.")
except Exception as e:
    print(f"Error initializing AssistantService: {e}")

print("\n=== Running Test Queries to Check Tool Activation ===")
test_queries = [
    "گوشی موبایل سامسونگ",
    "دسته‌بندی‌های کالاها را نشان بده",
    "محصولات زیر ۱۰ میلیون تومان",
    "مشابه محصول 123 را پیدا کن"
]

for query in test_queries:
    print(f"\nQuery: '{query}'")
    try:
        # تست تحلیل ابزارها بدون نیاز به اجرای کامل یا با اجرای تست ایمن
        messages = [
            {"role": "system", "content": "You are a helpful assistant for Digikala."},
            {"role": "user", "content": query}
        ]
        response = service.llm.invoke(messages)
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"  -> Activated Tools: {[tc['name'] for tc in response.tool_calls]}")
        else:
            print("  -> No tools activated directly by model (Direct text response or clarification).")
    except Exception as e:
        print(f"  -> Error testing query: {e}")
