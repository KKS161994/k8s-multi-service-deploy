from fastapi import FastAPI, HTTPException
import os
import redis

app = FastAPI()

REDIS_HOST = os.environ.get("REDIS_HOST","localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT","6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=2,
)

@app.get("/healthz")
def healthz() -> dict[str,str]:
    try:
        redis_client.ping()
        return {"status":"ok","redis":"ok"}
    except redis.RedisError:
        raise HTTPException(status_code=503, detail="redis unavailable")
    
@app.get("/stats/{code}")
def stats(code:str) -> dict[str, str | int]:
    url = redis_client.get(f"url:{code}")
    if url is None:
        raise HTTPException(status_code=404, detail="code not found")
    clicks = redis_client.get(f"clicks:{code}")
    return {
        "code": code,
        "url": url,
        "clicks": int(clicks) if clicks else 0,
    }

@app.get("/allstats")
def all_stats()->dict[str,list]:
    results = []
    for key in redis_client.scan_iter(match="url:*"):
        code = key.removeprefix("url:")
        url = redis_client.get(key)
        clicks = redis_client.get(f"clicks:{code}")
        results.append({
            "code": code,
            "url":url,
            "clicks":int(clicks) if clicks else 0,
            }
        )
    return {"entries":results}

    