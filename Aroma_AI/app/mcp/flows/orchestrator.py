import json
from app.core.redis_services import redis_client
from mcp.agents.manager_agent import manager_agent
from mcp.agents.welcome_agent import welcome_agent
from mcp.agents.table_allocation_agent import table_allocation_agent
from mcp.agents.order_manager_agent import order_manager_agent
from mcp.agents.billing_agent import billing_agent
from mcp.agents.delivery_manager_agent import delivery_manager_agent
from mcp.agents.feedback_agent import feedback_agent

from app import crud  # <-- your CRUDQna instance



# ---------------- STATE HANDLING ----------------
def load_state(user_id):
    raw = redis_client.get(f"conversation_state:{user_id}")
    return json.loads(raw) if raw else {
        "user_id": user_id,
        "current_agent": "Welcome_Agent",
        "collected_data": {}
    }

def save_state(user_id, state):
    try:
        redis_client.set(
            f"conversation_state:{user_id}",
            json.dumps(state),
            ex=60 * 60 * 3  # 3h expiry
        )
    except Exception as e:
        print(f"Redis save error: {e}")
# def save_history(user_id, query, answer, db):
#     """Save chat history in Redis + DB"""
#     redis_key = f"chat_history:{user_id}"
#     history = []

#     # Load old
#     past_data = redis_client.get(redis_key)
#     if past_data:
#         history = json.loads(past_data)

#     # Append new
#     history.append({"role": "user", "content": query})
#     history.append({"role": "agent", "content": answer})

#     # Save Redis with expiry
#     redis_client.setex(redis_key, 60 * 60 * 3, json.dumps(history))

#     # Save DB
#     try:
#         new_entry = ChatData(user_id=user_id, question=query, answer=answer)
#         db.add(new_entry)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         print(f"DB error storing chat: {e}")

# ---------------- MAIN ORCHESTRATION ----------------
def run_flow(user_id: str, user_message: str, db):
    state = load_state(user_id)
    history = crud.qna.get_user_chat_history(user_id, db)
    history.append({"role": "user", "content": user_message})

    # Decide routing with Manager
    decision = manager_agent(user_message, state,history=history)
    next_agent = decision.get("next_agent", "Welcome_Agent")
    state["current_agent"] = next_agent

    print(f"➡️ Routing to: {next_agent}")

    # Call correct agent
    if next_agent == "Welcome_Agent":
        resp = welcome_agent(user_message)
        msg = resp.get("prompt", "👋 Hello! How can I help you today?")

    elif next_agent == "Table_Allocation_Agent":
        resp = table_allocation_agent(user_message)
        state["collected_data"]["table"] = resp.get("table_details", {})
        msg = resp.get("prompt") or " ".join(resp.get("follow_up", []))

    elif next_agent == "Order_Manager_Agent":
        resp = order_manager_agent(user_message)
        state["collected_data"].setdefault("orders", [])
        state["collected_data"]["orders"].append(resp.get("order_details", {}))
        msg = resp.get("prompt") or " ".join(resp.get("follow_up", []))

    elif next_agent == "Billing_Agent":
        resp = billing_agent(user_message)
        state["collected_data"]["billing"] = resp.get("bill_details", {})
        msg = resp.get("prompt") or " ".join(resp.get("follow_up", []))

    elif next_agent == "Delivery_Manager_Agent":
        resp = delivery_manager_agent(user_message)
        state["collected_data"]["delivery"] = resp.get("delivery_details", {})
        msg = resp.get("prompt") or " ".join(resp.get("follow_up", []))

    elif next_agent == "Feedback_Agent":
        resp = feedback_agent(user_message)
        state["collected_data"]["feedback"] = resp.get("feedback", {})
        msg = resp.get("prompt") or " ".join(resp.get("follow_up", []))

    else:
        resp = {"prompt": f"❌ Agent {next_agent} not implemented."}
        msg = resp["prompt"]

    # Save history
    crud.qna.store_user_qa(db,user_id, user_message, msg)

    # Save state
    save_state(user_id, state)

    return {
        "agent": next_agent,
        "message": msg,
        "collected_data": state["collected_data"],
        "next_agent": next_agent
    }


if __name__ == "__main__":
    user_id = "U001"
    print("🍽️ Aroma AI Manager running. Type 'quit' to exit.")
    while True:
        msg = input("Customer: ")
        if msg.lower() in ["quit", "exit"]:
            break
        response = run_flow(user_id, msg, db=None)  # pass db in real app
        print("System:", response)
