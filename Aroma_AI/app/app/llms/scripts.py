import json
import random
from groq import Groq

# =======================
# Groq Client
# =======================
client = Groq(api_key="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")

# Default model config
default_model = "meta-llama/llama-4-scout-17b-16e-instruct"
default_max_tokens = 200


# =======================
# Safe LLM Call
# =======================
def llm(system_prompt, user_prompt, role, model, max_tokens, schema, temp=0):
    """Generic LLM call with enforced JSON schema and safe error handling."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"You are a {role}. {user_prompt}. "
                               f"Ensure JSON strictly matches this schema: {schema}. "
                               f"No extra keys, no deviations."
                }
            ],
            model=model,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            temperature=temp
        )
        raw_output = chat_completion.choices[0].message.content

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON from model", "raw_output": raw_output}

    except Exception as e:
        return {"error": str(e)}



with open("llms/prompt_templates.json", "r") as f:
    config = json.load(f)


def prompt_generation(role, query):
    system_prompt = config[role]["prompt"]
    user_prompt = query
    return system_prompt, user_prompt


def call_agent(role, query):
    """Call a specific agent safely."""
    try:
        system_prompt, user_prompt = prompt_generation(role, query)
        model = config[role].get("model", default_model)
        max_tokens = config[role].get("max_tokens", default_max_tokens)
        schema = config[role]["schema"]

        response = llm(system_prompt, user_prompt, role, model, max_tokens, schema)
        if "error" in response:
            print(f"[ERROR in {role}] →", response)
        return response
    except Exception as e:
        return {"error": f"Agent {role} failed: {str(e)}"}



def handle_followups(agent_name, initial_query):
    """Handle follow-ups until they are resolved."""
    response = call_agent(agent_name, initial_query)
    follow_count = 0

    while response.get("follow_up", []) and follow_count < 3:
        print(f"[{agent_name}] Follow-up:", response["follow_up"])
        user_input = input("Your answer: ")
        follow_count += 1
        new_query = f"Previous query: {initial_query}. Follow-up Q: {response['follow_up']}. Customer answered: {user_input}"
        response = call_agent(agent_name, new_query)

    return response



def delivery_assignment(order_id, user_id):
    """Randomly assign a delivery person from the available pool."""
    delivery_boys = ["Parth Bhai", "OG Sanskar Bhai", "Achal Bhai"]
    assigned = random.choice(delivery_boys)

    return {
        "name": "Delivery_Agent",
        "delivery_details": {
            "delivery_id": f"DEL-{order_id}",
            "assigned_to": assigned,
            "user_id": user_id,
            "status": "dispatched"
        },
        "follow_up": []
    }


def flow(query, user_input=None, current_agent=None, step=0):
    """
    Stateless flow handler for API usage.
    - query: starting query / prompt
    - user_input: last user ka answer
    - current_agent: kaunsa agent abhi active hai
    - step: flow ka current step
    """
    if current_agent is None:
        # Start of conversation
        response = call_agent("Welcome_Agent", query)
        return {
            "agent": response.get("name"),
            "task": response.get("prompt", ""),
            "follow_up": response.get("follow_up", []),
            "step": 1
        }

    elif current_agent == "Table_Allocation_Agent":
        new_query = f"{query} | User answered: {user_input}"
        response = call_agent("Table_Allocation_Agent", new_query)
        return {
            "agent": "Table_Allocation_Agent",
            "data": response,
            "follow_up": response.get("follow_up", []),
            "step": step + 1
        }

    elif current_agent == "Order_Manager_Agent":
        new_query = f"{query} | User answered: {user_input}"
        response = call_agent("Order_Manager_Agent", new_query)
        return {
            "agent": "Order_Manager_Agent",
            "data": response,
            "follow_up": response.get("follow_up", []),
            "step": step + 1
        }

    elif current_agent == "Feedback_Agent":
        response = call_agent("Feedback_Agent", user_input)
        return {
            "agent": "Feedback_Agent",
            "data": response,
            "follow_up": [],
            "step": step + 1
        }

    else:
        return {"error": f"Unknown agent {current_agent}"}
