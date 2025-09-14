
import logging
import re
import json
import string
from sqlalchemy import text
from datetime import date, datetime, timedelta
import json
from sqlalchemy.orm import Session
from app.db.base import Base
from app.core.redis_services import redis_client
# from app.vector_store.pgvector_llama_index import VectorStorePostgresVector
# from app.embeddings.embedding import huggingface_embeddings
from mcp.flows.orchestrator import run_flow
# from app.models.user import Users,Company,UserTypesMaster, QnA, FAQ
from app.models.chat import ChatData
from app.models.user import User
# from app.models.faq import FAQ
# from app.utils.doc_summary import merge_summary
# from app.core.agent_pool_config import agent_settings
# from app.utils.llm_instance import get_instance_answer
# from app.utils.chat_services import chat_obj
# from app.core.security import authentication



_logger = logging.getLogger(__name__)


import uuid

SESSION_TTL = 3600  # 1 hour



class CRUDQna:
    def all_chat_history(self, user_id: str, db, all_chat=True) -> list:
        history_query = (
                db.query(ChatData)
                .filter(ChatData.user_id == user_id)
                .order_by(ChatData.createdon.asc())
            )

        if not all_chat:
            today = datetime.utcnow().date()  
            start_of_today = datetime.combine(today, datetime.min.time())
            start_of_tomorrow = start_of_today + timedelta(days=1)

            history_query = history_query.filter(
                ChatData.modifiedon >= start_of_today,
                ChatData.modifiedon < start_of_tomorrow
            )

        history_db = history_query.all()
        
        history = []
        for row in history_db:
            history.extend([
                {"role": "user", "content": row.question},
                {"role": "assistant", "content": row.answer}
            ])
        return history

    def get_user_chat_history(self, user_id: str, db) -> list:
        """
        Retrieve the user's recent chat history.
        First attempts to get it from Redis cache (today's key),
        then falls back to the DB if not found.
        """
        redis_key_today = f"chat_history:{user_id}"
        redis_key_yesterday = f"chat_history:{user_id}"

        history = []

        try:
            past_data = redis_client.get(redis_key_today)
            if past_data:
                history = json.loads(past_data)
                value=8
                return history[-(int(value)):] if len(history) >= int(value) else history
            _logger.info(f"Redis key not found for today's chat: {redis_key_today}")
            redis_client.delete(redis_key_yesterday)
        except Exception as e:
            _logger.warning(f"Redis error while fetching history for {redis_key_today}: {e}")

        # Fallback: Fetch from DB
        try:
            history_db = (
                db.query(ChatData)
                .filter(ChatData.user_id == user_id)
                .order_by(ChatData.created_at.asc())
                .limit(8)
                .all()
            )
            for row in history_db:
                history.extend([
                    {"role": "user", "content": row.question},
                    {"role": "assistant", "content": row.answer}
                ])

            try:
                redis_client.set(redis_key_today, json.dumps(history))
                _logger.info(f"Stored chat history to Redis: {redis_key_today}")
            except Exception as e:
                _logger.warning(f"Redis write failed for key {redis_key_today}: {e}")

        except Exception as e:
            _logger.error(f"Database error fetching chat history for user {user_id}: {e}")
        return history

    def store_user_qa(self, db: Session, user_id: str, query: str, answer) -> None:
        """
        Store the new question-answer pair to Redis + DB.
        - Reads existing history from Redis.
        - Appends new Q&A to it.
        - Handles both string and structured (dict/list) answers.
        """

        today = date.today().isoformat()
        redis_key = f"chat_history:{user_id}"
        # Step 1: Try to fetch and parse existing history
        try:
            cached_history = redis_client.get(redis_key)
            if cached_history:
                try:
                    history = json.loads(cached_history)
                    if not isinstance(history, list):
                        _logger.warning(f"Invalid history format in Redis for key {redis_key}, resetting.")
                        history = []
                except json.JSONDecodeError:
                    _logger.warning(f"Corrupted history in Redis for key {redis_key}, resetting.")
                    history = []
            else:
                history = []
        except Exception as e:
            _logger.warning(f"Error reading Redis key {redis_key}: {e}")
            history = []

        if isinstance(answer, (dict, list)):
            answer_to_store = json.dumps(answer)
        else:
            answer_to_store = str(answer)
        history.extend([
            {"role": "user", "content": query},
            {"role": "assistant", "content": answer_to_store}
        ])
        try:
            redis_client.set(redis_key, json.dumps(history), ex=60*60*3)
            _logger.info(f"Stored Q&A in Redis for user {user_id}")
        except Exception as e:
            _logger.warning(f"Failed to write Q&A to Redis for key {redis_key}: {e}")
            # Store in DB
        try:
            new_entry = ChatData(user_id=user_id,question=query, answer=f"{answer}")
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            _logger.info(f"Stored Q&A in DB for user {user_id}, entry_id={new_entry.id}")
        except Exception as e:
            db.rollback()
            _logger.error(f"Failed to store Q&A in DB for user {user_id}: {e}")


    async def ask_qna(self, db: Session, current_user, params) -> dict:
        # try:
        if not params.query:
            return {
                "success": False,
                "msg": "Query parameter is not provided",
                "data": None
            }
        query = params.query
        normalized_query = query.translate(str.maketrans('', '', string.punctuation))
        normalized_query = normalized_query.strip().replace(" ", "").lower()
        if redis_client.exists(normalized_query):
            answer = redis_client.get(normalized_query)
            if isinstance(answer, bytes):
                answer = answer.decode("utf-8")
            _logger.info(f"Cache hit for query: '{normalized_query}'")
            return {
                "success": True,
                "msg": "Fetched from cache",
                "data": {
                    "answer": answer,
                    "type": "text",
                    "user_id": current_user.id,
                    "docs_details": [],
                    "quick_replies": []
                }
            }
        history = self.get_user_chat_history(current_user.id, db)
        final_answer = run_flow(current_user.id, query, db)
        if isinstance(final_answer, dict) and "error" not in final_answer:
            answer_text = json.dumps(final_answer, ensure_ascii=False)
        else:
            answer_text = run_flow(current_user.id, history, db)
        # final_answer = str(final_answer)
        # self.store_user_qa(db, current_user.id, query, answer_text)
        # redis_client.set(normalized_query, answer_text)
        return {
            "success": True,
            "msg": "Response generated",
            "data": {
                "answer": answer_text,
                "type": "text",
                "user_id": current_user.id,
                "docs_details": [],
                "quick_replies": []
            }
        }

        # except Exception as e:
        #     _logger.error(f"Error in ask_qna: {e}")
        #     return {"success": False, "msg": str(e), "data": None}
    
    def start_session(self, user_id, query):
        session_id = str(uuid.uuid4())
        state = flow(query)

        # Session state Redis me save
        redis_client.set(
            f"session:{user_id}:{session_id}",
            json.dumps(state),
            ex=SESSION_TTL
        )

        # Empty chat history create karo
        redis_client.delete(f"chat_history:{user_id}")
        redis_client.rpush(
            f"chat_history:{user_id}",
            json.dumps({"query": query, "state": state})
        )
        redis_client.expire(f"chat_history:{user_id}", SESSION_TTL)

        return session_id, state

    def continue_session(self, user_id, session_id, query, user_input="", current_agent=None, step=1):
        # Flow ke andar jao with current state
        state = run_flow(query, user_input, current_agent, step)

        # Update session current state
        redis_client.set(
            f"session:{user_id}:{session_id}",
            json.dumps(state),
            ex=SESSION_TTL
        )

        # Chat history me append karo
        redis_client.rpush(
            f"chat_history:{user_id}",
            json.dumps({"query": query, "user_input": user_input, "state": state})
        )
        redis_client.expire(f"chat_history:{user_id}", SESSION_TTL)

        return state

    def get_session(self, user_id, session_id):
        raw = redis_client.get(f"session:{user_id}")
        if raw:
            return json.loads(raw)
        return None

    def get_chat_history(self, user_id, session_id):
        # Puri history list fetch karo
        raw_list = redis_client.lrange(f"chat_history:{user_id}", 0, -1)
        return [json.loads(item) for item in raw_list] if raw_list else []
            
qna = CRUDQna()