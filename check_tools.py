import sys
import os

print("Checking Assistant Routes and LLM Service...")
if os.path.exists("api/routes/assistant.py"):
    with open("api/routes/assistant.py", "r", encoding="utf-8") as f:
        print("--- api/routes/assistant.py snippet ---")
        print("".join(f.readlines()[:100]))

if os.path.exists("src/llm/service.py"):
    with open("src/llm/service.py", "r", encoding="utf-8") as f:
        print("--- src/llm/service.py snippet ---")
        print("".join(f.readlines()[:100]))
