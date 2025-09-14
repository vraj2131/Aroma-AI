import json
from ..connectors.llm_client import llm_call
from mcp.prompts.prompt_config import PROMPT_CONFIG


def table_allocation_agent(task_prompt: str):
    """
    Table Allocation Agent: helps the customer reserve or allocate a table.
    Fetches config from PROMPT_CONFIG.
    """

    config = PROMPT_CONFIG.get("Table_Allocation_Agent", {})
    system_prompt = config.get("prompt", "")
    schema = config.get("schema", {})
    model = config.get("model")
    max_tokens = config.get("max_tokens", 150)

    # Call the LLM with schema validation
    response = llm_call(
        system_prompt=system_prompt,
        user_prompt=task_prompt,
        role="Table_Allocation_Agent",
        model=model,
        max_tokens=max_tokens,
        schema=schema,
    )
    print('table agent response', response)
    # If response is already a dict, don't parse it again
    if isinstance(response, str):
        return json.loads(response)
    elif isinstance(response, dict):
        return response
        

    try:
        print('table agent response',response)
        if isinstance(response, str):
            return json.loads(response)
        elif isinstance(response, dict):
            return response
    except Exception:
        return {
            "name": "Table_Allocation_Agent",
            "table_details": {
                "table_id": "TAB-UNKNOWN",
                "user_id": "",
                "status": "unallocated",
                "number_of_guests": 0,
                "time": "",
                "date": ""
            },
            "follow_up": [
                "⚠️ Sorry, I couldn’t process your table request. Could you provide the number of guests and preferred time again?"
            ]
        }
