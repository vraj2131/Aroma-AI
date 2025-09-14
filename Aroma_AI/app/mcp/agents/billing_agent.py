import json
from ..connectors.llm_client import llm_call
from mcp.prompts.prompt_config import PROMPT_CONFIG


def billing_agent(task_prompt: str):
    """
    Billing Agent: generates bill details using LLM.
    Fetches config from PROMPT_CONFIG.
    """

    config = PROMPT_CONFIG.get("Billing_Agent", {})
    system_prompt = config.get("prompt", "")
    schema = config.get("schema", {})
    model = config.get("model")
    max_tokens = config.get("max_tokens", 150)

    # Call the LLM with strict schema
    response = llm_call(
        system_prompt=system_prompt,
        user_prompt=task_prompt,
        role="Billing_Agent",
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
            "bill_details": {
                "bill_id": "BILL-ERR",
                "order_id": "UNKNOWN",
                "amount": "0",
                "payment_method": "",
                "status": "FAILED"
            },
            "follow_up": ["⚠️ Sorry, I could not generate your bill. Please try again."]
        }
