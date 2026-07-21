from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from diff_engine import compute_diff, tokenize_simple


app = FastAPI()


class DiffRequest(BaseModel):
    left: str
    right: str


class TokenizeRequest(BaseModel):
    text: str


@app.get("/health")
async def health():
    return {"status": "ok", "port": 8009}


@app.post("/diff")
async def diff(request: DiffRequest):
    result = compute_diff(request.left, request.right)
    return result


@app.post("/tokenize")
async def tokenize(request: TokenizeRequest):
    token_count = tokenize_simple(request.text)
    char_count = len(request.text)
    return {"token_count": token_count, "char_count": char_count}


@app.get("/")
async def root():
    return FileResponse("static/index.html")


static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
