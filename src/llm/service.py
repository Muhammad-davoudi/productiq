import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from src.llm import adapter

load_dotenv(find_dotenv())

# جمع‌آوری ابزارهای موجود در adapter
ALL_TOOLS = [
    adapter.search_products,
    adapter.get_categories,
    adapter.search_by_price,
    adapter.search_exact,
    adapter.recommend_similar_products
]

TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

class AssistantService:
    def __init__(self):
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")

        init_kwargs = {
            "model": model_name,
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.0")),
        }
        if api_key:
            init_kwargs["openai_api_key"] = api_key
        if base_url:
            init_kwargs["openai_api_base"] = base_url

        base_llm = ChatOpenAI(**init_kwargs)
        # اتصال همیشگی ابزارها به مدل با استفاده از bind_tools
        self.llm = base_llm.bind_tools(ALL_TOOLS)

    def process_input(self, session_id: str, user_input: str) -> str:
        system_prompt = (
            "You are a helpful assistant for Digikala. "
            "STRICT RULES: "
            "1. Do not use asterisks (*) or any markdown formatting like bold/italic for text under any circumstances. "
            "2. Use plain text only. "
            "3. When presenting product suggestions, lists, or multiple items, you MUST output them line-by-line using bullet points (e.g. using dash - or numbers) and keep them structured vertically, never inline. "
            "4. If a user asks for a general product without details (e.g., a good phone), "
            "ask clarifying questions about budget, brand, and features rather than failing or assuming random items. "
            "5. Use the provided tools when specific products or categories are requested. "
            "6. After receiving tool outputs, you MUST synthesize the results into a helpful, clear, and direct Persian response for the user without returning empty text."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        response = self.llm.invoke(messages)

        # بررسی اینکه آیا مدل ابزاری را فراخوانی کرده است یا خیر
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"[TOOL USAGE LOG] Model called tools: {[tc['name'] for tc in response.tool_calls]}")
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_func = TOOL_MAP.get(tool_name)

                if tool_func:
                    try:
                        # استفاده از invoke برای اجرای صحیح StructuredTool در LangChain
                        tool_output = tool_func.invoke(tool_args)
                    except Exception as e:
                        tool_output = f"Error executing tool: {e}"
                else:
                    tool_output = f"Tool {tool_name} not found."

                messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))

            final_response = self.llm.invoke(messages)
            if final_response and final_response.content and final_response.content.strip():
                return final_response.content
            return f"نتایج یافت شده: {str(tool_output)}"

        if response and response.content and response.content.strip():
            return response.content
        return "پاسخی دریافت نشد."
