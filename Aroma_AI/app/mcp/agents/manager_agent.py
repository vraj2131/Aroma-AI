import json
from ..connectors.llm_client import llm_call
from mcp.prompts.prompt_config import PROMPT_CONFIG
from mcp.tools import get_tool_info

def manager_agent(user_message: str, state: dict = None, history: list = None) -> dict:
    """LLM router with conversation history context."""
    config = PROMPT_CONFIG["Manager_Agent"]

    context = {
        "history": history[-6:] if history else [{"role": "user", "content": user_message}],
        "current_agent": state.get("current_agent") if state else None
    }
    print('manager_context:',context)

    response = llm_call(
        system_prompt=config["prompt"],
        user_prompt=json.dumps(context, ensure_ascii=False),
        role="Manager_Agent",
        model=config["model"],
        max_tokens=config["max_tokens"],
        schema=config["schema"],
        Tool_context=get_tool_info("Manager_Agent")
    )

    if isinstance(response, str):
        try:
            return json.loads(response)
        except Exception:
            return {"next_agent": "Welcome_Agent"}
    elif isinstance(response, dict):
        return response
    return {"next_agent": "Welcome_Agent"}

