from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from uvicorn.workers import UvicornWorker

import sys

sys.path.append('../')

from app.api.api_v1.api import api_router
from app.core.config import settings

load_dotenv(verbose=True)
app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs", redoc_url="/redoc",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "log_config": "./logging_config.yaml",
    }
