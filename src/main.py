# ruff: noqa: E402
import sys
from pathlib import Path
import logging

from fastapi import FastAPI
import uvicorn

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)

from src.CRUD.auth import router as router_auth


app = FastAPI()

app.include_router(router_auth)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
