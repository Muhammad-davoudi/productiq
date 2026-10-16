import sys
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

print("API Key present:", bool(os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")))
print("Base URL:", os.getenv("LLM_BASE_URL"))

try:
    from src.llm.service import AssistantService, ALL_TOOLS
    print("\n=== Checking LLM Tools Binding ===")
    print(f"Total bound tools: {len(ALL_TOOLS)}")
    for tool in ALL_TOOLS:
        print(f" - Tool Name: {tool.name}, Description: {tool.description}")

    service = AssistantService()
    print("\nAssistantService initialized successfully.")

    test_queries = [
        "گوشی موبایل سامسونگ",
        "دسته‌بندی‌های کالاها را نشان بده",
        "محصولات زیر ۱۰ میلیون تومان",
        "مشابه محصول 123 را پیدا کن"
    ]

    print("\n=== Running Test Queries to Check Tool Activation ===")
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant for Digikala."},
                {"role": "user", "content": query}
            ]
            response = service.llm.invoke(messages)
            if hasattr(response, "tool_calls") and response.tool_calls:
                print(f"  -> Activated Tools: {[tc['name'] for tc in response.tool_calls]}")
            else:
                print(f"  -> Response content: {getattr(response, 'content', str(response))}")
        except Exception as e:
            print(f"  -> Error testing query: {e}")

except Exception as e:
    print(f"Initialization or import error: {e}")
