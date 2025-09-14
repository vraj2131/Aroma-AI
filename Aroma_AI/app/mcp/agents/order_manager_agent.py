import json
from ..connectors.llm_client import llm_call
from mcp.prompts.prompt_config import PROMPT_CONFIG


def order_manager_agent(task_prompt: str):
    """
    Order Manager Agent: helps the customer place their food order.
    Fetches config from PROMPT_CONFIG.
    """

    config = PROMPT_CONFIG.get("Order_Manager_Agent", {})
    system_prompt = config.get("prompt", "")
    schema = config.get("schema", {})
    model = config.get("model")
    max_tokens = config.get("max_tokens", 200)

    # Call LLM with schema enforcement
    print('user_prompt:',task_prompt)
    
    response = llm_call(
        system_prompt=system_prompt,
        user_prompt=task_prompt,
        role="Order_Manager_Agent",
        model=model,
        max_tokens=max_tokens,
        schema=schema,
    )

    try:
        if isinstance(response, str):
            return json.loads(response)
        elif isinstance(response, dict):
            return response
    except Exception:
        return {
            "name": "Order_Manager_Agent",
            "order_details": {
                "order_id": "ORD-UNKNOWN",
                "table_id": "",
                "user_id": "",
                "status": "pending"
            },
            "follow_up": [
                "⚠️ Sorry, I couldn’t process your order properly. Could you rephrase it?"
            ]
        }
