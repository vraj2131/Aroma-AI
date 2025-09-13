import os
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import (AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn,
                      validator)

load_dotenv(verbose=True)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "s9dF8gH7jKl3Pq2R1tUvWxYz0!@#4bN6mQ"
    PROJECT_NAME: str = "AromaAI"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 3
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    OTP_VALIDITY_MINUTES: int = 10
    
    DOCUMENT_SUPPORTED_EXTENSIONS_MAPPING : dict = {
        'Word': {'doc', 'docx'},
        'Power Point': {'pptx'},
        'Markdown': {'md'},
        'PDF': {'pdf'},
        'CSV': {'csv'},
        'Excel': {'xls', 'xlsx'},
        'Image': {'png', 'jpg', 'jpeg'},
        'Transcript': {'srt'},
        'Unstructured File': {'txt'}
    }
    GOOGLE_DRIVE_CREDENTIAL_BUCKET_NAME : str = os.getenv("GOOGLE_DRIVE_CREDENTIAL_BUCKET_NAME")
    GOOGLE_DRIVE_KEYS_BASE_FOLDER : str = os.getenv("GOOGLE_DRIVE_KEYS_BASE_FOLDER")
    DRIVE_READ_ONLY_ACCESS = 'https://www.googleapis.com/auth/drive.readonly'
    VECTOR_CONNECTION_STRING: str = os.getenv("VECTOR_CONNECTION_STRING","postgresql://postgres:postgres@192.168.0.169:5432/goose_ai_db")

settings = Settings()