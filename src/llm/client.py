import os
import yaml
from pathlib import Path
from typing import Optional, List, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage

load_dotenv()

CONFIG_PATH = Path("config/llm_config.yaml")

def load_llm_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def get_llm_client(temperature: Optional[float] = None, timeout: Optional[float] = None):
    config = load_llm_config().get("llm", {})
    provider_var = config.get("provider_env_var", "PROVIDER")
    provider = os.getenv(provider_var, os.getenv("LLM_PROVIDER", config.get("default_provider", "openai"))).lower()

    api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    base_url = os.getenv("LLM_BASE_URL", None)
    model_name = os.getenv("LLM_MODEL", config.get("default_model", "gpt-4o-mini"))

    t = temperature if temperature is not None else float(config.get("temperature", 0.0))
    to = timeout if timeout is not None else float(config.get("request_timeout", 15.0))
    retries = int(config.get("max_retries", 2))

    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key or "placeholder_key",
        base_url=base_url if base_url else None,
        temperature=t,
        timeout=to,
        max_retries=retries,
    )

class LLMClient:
    def __init__(self):
        self.client = get_llm_client()

    def get_model_with_tools(self, tools: List[Any]):
        return self.client.bind_tools(tools)
