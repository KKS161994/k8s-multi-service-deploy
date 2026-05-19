from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import string 
import random
import redis
import os

app = FastAPI()

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=2,
)

# In-memory store. Will move to Redis once the cluster has a backing service.
store: dict[str, str] = {}


class ShortUrlRequest(BaseModel):
    url:str

def generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/shorten", response_model=dict[str, str])
def shortenRequest(request: ShortUrlRequest)->dict[str, str]:
    code = generate_code()

    while not redis_client.set(f"url:{code}", request.url, nx=True):
        code = generate_code()
    
    store[code] = request.url
    return {"code":code, "url":request.url}

@app.get("/healthz",response_model=dict[str,str])
def healthz():
    try:
        redis_client.ping()
        return {"status": "ok", "redis": "ok"}
    except redis.RedisError:
        raise HTTPException(status_code=503, detail="redis unavailable")



@app.get("/r/{code}",response_model=dict[str,str])
def resolve(code: str):
    url = redis_client.get(f"url:{code}")
    if url is None:
        raise HTTPException(status_code=404, detail="code not found")
    redis_client.incr(f"clicks:{code}")
    return {"code":code,"url":store[code]}