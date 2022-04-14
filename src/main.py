import logging
import uvicorn as uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core import config
from core.logger import LOGGING
from database.db import engine, Base
from api.v1 import auth, todos

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
