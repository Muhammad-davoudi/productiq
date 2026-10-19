from src.llm import adapter
from src.llm.service import ALL_TOOLS, TOOL_MAP

print("--- ALL_TOOLS NAMES ---")
for t in ALL_TOOLS:
    print(f"- Name: {t.name}, Func: {t.func.__name__ if hasattr(t, 'func') else t.__name__}")

print("\n--- TOOL_MAP KEYS ---")
for k in TOOL_MAP.keys():
    print(f"- {k}")
