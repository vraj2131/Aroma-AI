import json
from ..connectors.llm_client import llm_call
from mcp.prompts.prompt_config import PROMPT_CONFIG
from mcp.tools import get_tool_info
def welcome_agent(user_message: str):
    config = PROMPT_CONFIG["Welcome_Agent"]
    response = llm_call(
        system_prompt=config["prompt"],
        user_prompt=user_message,
        role="Welcome_Agent",
        model=config["model"],
        max_tokens=config["max_tokens"],
        schema=config["schema"],
        Tool_context=get_tool_info("Welcome_Agent")
    )
    try:
        if isinstance(response, str):
            return json.loads(response)
        elif isinstance(response, dict):
            return response
    except Exception:
        return {"prompt": "👋 Hello! How can I help you today?"}
