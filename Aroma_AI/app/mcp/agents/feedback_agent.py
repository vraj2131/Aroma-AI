import json
from ..connectors.llm_client import llm_call
from mcp.prompts.prompt_config import PROMPT_CONFIG


def feedback_agent(feedback_text: str):
    """
    Feedback Agent: collects customer feedback and sentiment.
    Fetches config from PROMPT_CONFIG.
    """

    config = PROMPT_CONFIG.get("Feedback_Agent", {})
    system_prompt = config.get("prompt", "")
    schema = config.get("schema", {})
    model = config.get("model")
    max_tokens = config.get("max_tokens", 150)

    # Call the LLM with strict schema
    response = llm_call(
        system_prompt=system_prompt,
        user_prompt=feedback_text,
        role="Feedback_Agent",
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
            "customer": {"response": feedback_text},
            "feedback": {
                "user_id": "UNKNOWN",
                "table_id": "",
                "order_id": "",
                "sentiment": "neutral"
            },
            "follow_up": [
                "⚠️ Sorry, I couldn’t process your feedback properly. Could you rephrase?"
            ]
        }
