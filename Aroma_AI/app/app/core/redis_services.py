import json
import logging
from redis import StrictRedis
from app.core.config import settings
from typing import Optional, Any

_logger = logging.getLogger(__name__)

class RedisClient:
    # def __init__(self, redis_host=settings.REDIS_HOST, redis_port=settings.REDIS_PORT, redis_db=settings.REDIS_DB):
    def __init__(self):
        self.redis_host = settings.REDIS_HOST
        self.redis_port = settings.REDIS_PORT
        self.redis_db = settings.REDIS_DB
        self.redis_client = StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db, decode_responses=True)

    def hget_state(self, key, data_key_name):
        value_json = self.redis_client.hget(key, data_key_name)
        if value_json:
            value = value_json.decode('utf-8')
            try:
                parsed_json = json.loads(value)
                return parsed_json
            except json.JSONDecodeError:
                return value
        return None
    
    def hset_state(self, key, key_name, value, expire_time=None):
        self.redis_client.hset(key, key_name, value)
        if expire_time is not None:
            self.redis_client.expire(key, expire_time)
        _logger.debug(f"{key}:{value}")
        
    def scan_keys(self, pattern):
        keys = self.redis_client.scan_iter(pattern)
        return [key for key in keys]
    
    def h_increment(self, key, field, amount,logger_request_id):
        try:
            return self.redis_client.hincrby(key, field, amount)
        except Exception as e:
            # _logger.error(f"Error incrementing field {field} in key {key}: {e}")
            _logger.error(
                        "error incrementing field in key",
                        exc_info=True,
                        extra={
                            "request_id": logger_request_id,
                            "error": str(e)
                        }
                    )
            return None
    def hgetall(self, key):
        try:
            hash_data = self.redis_client.hgetall(key)
            hash_data = {k: v for k, v in hash_data.items()}
            return hash_data
        except Exception as e:
            _logger.error(f"Failed to get hash: {e}")
            #  _logger.error(
            #             "error incrementing field in key",
            #             exc_info=True,
            #             extra={
            #                 "request_id": logger_request_id,
            #                 "error": str(e)
            #             }
            #         )
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key (str): The Redis key to check.

        Returns:
            bool: True if key exists, False otherwise.
        """
        try:
            result = self.redis_client.exists(key)
            _logger.debug(f"Exists check for key '{key}': {bool(result)}")
            return bool(result)
        except Exception as e:
            _logger.error(f"Error checking existence of key '{key}' in Redis: {e}")
            return False
        
    def flush_db(self) -> None:
        """
        Delete all keys in the selected Redis database.

        WARNING: This will remove all data from the database.
        """
        try:
            self.redis_client.flushdb()
            _logger.warning("Redis database flushed.")
        except Exception as e:
            _logger.error(f"Error flushing Redis database: {e}")
            
    def delete(self, key: str) -> int:
        """
        Delete a key from Redis.

        Args:
            key (str): The Redis key to delete.

        Returns:
            int: The number of keys that were removed.
        """
        try:
            result = self.redis_client.delete(key)
            _logger.debug(f"Deleted key: {key} | Deleted count: {result}")
            return result
        except Exception as e:
            _logger.error(f"Error deleting key '{key}' from Redis: {e}")
            return 0
        
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set a value in Redis with optional expiration.

        Args:
            key (str): The Redis key.
            value (Any): The value to store (will be JSON serialized).
            ex (Optional[int]): Expiration time in seconds. Defaults to None.

        Returns:
            bool: True if set was successful, False otherwise.
        """
        try:
            value = json.dumps(value)
            result = self.redis_client.set(key, value, ex=ex)               
            _logger.debug(f"Set key: {key} | Expires in: {ex}s")
            return result
        except Exception as e:
            _logger.error(f"Error setting key '{key}' in Redis: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis and deserialize from JSON.

        Args:
            key (str): The Redis key.

        Returns:
            Optional[Any]: The retrieved value or None if not found or error.
        """
        try:
            value = self.redis_client.get(key)
            if value is not None:
                _logger.debug(f"Retrieved key: {key}")
                return json.loads(value)
            _logger.debug(f"Key not found: {key}")
            return None
        except Exception as e:
            _logger.error(f"Error getting key '{key}' from Redis: {e}")
            return None

redis_client = RedisClient()