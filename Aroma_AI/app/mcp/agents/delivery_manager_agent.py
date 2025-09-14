import json
from ..connectors.llm_client import llm_call
from mcp.prompts.prompt_config import PROMPT_CONFIG
from mcp.tools import get_tool_info


def delivery_manager_agent(task_prompt: str):
    """
    Delivery Manager Agent: arranges delivery for online orders.
    Fetches config from PROMPT_CONFIG.
    """
    tool_context=get_tool_info("Delivery_Manager_Agent")

    config = PROMPT_CONFIG.get("Delivery_Manager_Agent", {})
    system_prompt = config.get("prompt", "")
    schema = config.get("schema", {})
    model = config.get("model")
    max_tokens = config.get("max_tokens", 200)

    # Call the LLM with strict schema
    response = llm_call(
        system_prompt=system_prompt,
        user_prompt=task_prompt,
        role="Delivery_Manager_Agent",
        model=model,
        max_tokens=max_tokens,
        schema=schema,
        Tool_context=tool_context,

    )

    try:
        if isinstance(response, str):
            return json.loads(response)
        elif isinstance(response, dict):
            return response
    except Exception:
        return {
            "delivery_details": {
                "delivery_id": "DEL-ERR",
                "order_id": "UNKNOWN",
                "status": "FAILED"
            },
            "follow_up": ["⚠️ Sorry, I could not process delivery details. Please try again."]
        }
