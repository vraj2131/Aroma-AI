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


def flow(query):
    role = "Welcome_Agent"
    # query = input("Customer: ")

    response1 = call_agent(role, query)

    if "error" in response1:
        print("[FATAL] Welcome Agent failed →", response1)
        exit()

    next_agent = response1.get("name", "").strip()
    if not next_agent:
        print("[ERROR] Welcome Agent did not return a valid 'name'. Full response:", response1)
        exit()

    print("Routing to:", next_agent)
    print("Task:", response1.get("prompt", ""))
    print("****************************************************")


    if next_agent == "Table_Allocation_Agent":
        table_response = handle_followups("Table_Allocation_Agent", response1.get("prompt", ""))
        print("Final Response:", table_response)

        order_response = handle_followups("Order_Manager_Agent", "Start taking order for this dine-in customer")
        print("Order Response:", order_response)

        feedback = input("Your task is completed. Please rate our services: ")
        feedback_response = call_agent("Feedback_Agent", feedback)
        print("Feedback Response:", feedback_response)


    elif next_agent == "Order_Manager_Agent":
        order_response = handle_followups("Order_Manager_Agent", response1.get("prompt", ""))
        print("Order Response:", order_response)

        # Delivery step added for takeaway
        delivery_response = delivery_assignment(
            order_response.get("order_details", {}).get("order_id", "NA"),
            order_response.get("order_details", {}).get("user_id", "NA")
        )
        print("Delivery Response:", delivery_response)

        feedback = input("Your takeaway order is completed. Please rate our services: ")
        feedback_response = call_agent("Feedback_Agent", feedback)
        print("Feedback Response:", feedback_response)


    elif next_agent == "Online_Order_Agent":
        order_response = handle_followups("Order_Manager_Agent", "Start taking online order")
        print("Order Response:", order_response)

        delivery_response = handle_followups("Delivery_Manager_Agent", "Arrange delivery for this order")
        print("Delivery Response:", delivery_response)

        feedback = input("Your online order & delivery are completed. Please rate our services: ")
        feedback_response = call_agent("Feedback_Agent", feedback)
        print("Feedback Response:", feedback_response)

    else:
        print("[ERROR] Unknown routing:", next_agent)
    return feedback_response
