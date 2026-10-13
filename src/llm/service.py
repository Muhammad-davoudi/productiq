import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.llm.adapter import (
    search_products,
    get_categories,
    search_by_price,
    search_exact,
    recommend_similar_products
)

load_dotenv(find_dotenv())

class AssistantService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            base_url=os.getenv("LLM_BASE_URL"),
            api_key=os.getenv("LLM_API_KEY"),
        )
        self.tools = [
            search_products,
            get_categories,
            search_by_price,
            search_exact,
            recommend_similar_products
        ]
        # ایجاد یک دیکشنری برای دسترسی راحت‌تر به ابزارها
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def process_input(self, session_id, user_input):
        system_prompt = (
            "You are a helpful assistant for Digikala. "
            "STRICT RULES: "
            "1. Do not use asterisks (*) or any markdown formatting like bold/italic for text. "
            "2. Use plain text only. "
            "3. If a tool output is provided, summarize it clearly without formatting characters. "
            "4. Return at most 5 items unless asked otherwise. "
            "5. If no products are found, be polite and helpful."
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]

        response = self.llm_with_tools.invoke(messages)

        if response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_name = tool_call['name']
            tool_args = tool_call['args']

            tool_to_use = self.tool_map.get(tool_name)

            if tool_to_use:
                # استفاده از invoke به جای فراخوانی مستقیم
                tool_output = tool_to_use.invoke(tool_args)

                messages.append(response)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(tool_output)
                })

                final_response = self.llm.invoke(messages)
                return final_response.content
            else:
                return "ابزار مورد نظر یافت نشد."

        return response.content
