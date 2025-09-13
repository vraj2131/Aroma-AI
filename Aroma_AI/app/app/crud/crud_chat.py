
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
from app.llms.scripts import flow
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
                value=redis_client.get("goose_ai_extra_config").get("greeting_history_count", 8)
                return history[-(int(value)):] if len(history) >= int(value) else history
            _logger.info(f"Redis key not found for today's chat: {redis_key_today}")
            redis_client.delete(redis_key_yesterday)
        except Exception as e:
            _logger.warning(f"Redis error while fetching history for {redis_key_today}: {e}")

        # Fallback: Fetch from DB
        try:
            # QnA = Base.classes.goose_chat_data
            history_db = (
                db.query(ChatData)
                .filter(ChatData.user_id == user_id)
                .order_by(ChatData.createdon.asc())
                .limit(3)
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

    def store_user_qa(self, db : Session, user_id: str, query: str, answer: str, history: list) -> None:
        """
        Store the new question-answer pair to Redis by appending to existing history.
        """
        today = date.today().isoformat()
        redis_key = f"chat_history:{user_id}:{today}"
        history.extend([
            {"role": "user", "content": query},
            {"role": "assistant", "content": answer}
        ])
        try:
            redis_client.set(redis_key, json.dumps(history))
            _logger.info(f"Appended new Q&A to Redis for user {user_id}")
        except Exception as e:
            _logger.warning(f"Failed to store Q&A in Redis for key {redis_key}: {e}")

        try:
            new_entry = ChatData(user_id=user_id,question=query, answer=answer)
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            _logger.info(f"Stored Q&A in DB for user {user_id}, entry_id={new_entry.id}")
        except Exception as e:
            db.rollback()
            _logger.error(f"Failed to store Q&A in DB for user {user_id}: {e}")
        finally:
            db.close()

    async def ask_qna(self, db: Session, current_user, params) -> dict:
        try:
            if not params.query:
                return {"success": False, "msg": "Query parameter is not provided", "data": None}
            params = {"query":params.query, "isnew":params.isnew}
            query = params.get("query")
            normalized_query = query.translate(str.maketrans('', '', string.punctuation))
            normalized_query = normalized_query.strip().replace(" ", "").lower()

            key_exists = redis_client.exists(normalized_query)
            if key_exists:
                answer = redis_client.get(normalized_query)       
                _logger.info(f"Cache hit for query: '{normalized_query}'")
                return {
                    "success": True,
                    "msg": "Existing response",
                    "data": {
                        "answer": answer,
                        "type": "text",
                        "user_id": current_user.id,
                        "docs_details": [],
                        "group_id": params.get("group_id"),
                        "quick_replies": []
                    }}

            history = self.get_user_chat_history(current_user.id, db)
            # history = []
            # TODO
            user_id=current_user.id
            final_answer = flow(params.get("query"))
            self.store_user_qa(db,current_user.id, params.get("query"), final_answer, history)
        except Exception as e:
            _logger.error(f"Error in ask_qna: {e}")
            return {"success": False, "msg": str(e), "data": None}
            
qna = CRUDQna()
