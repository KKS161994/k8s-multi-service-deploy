from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import string 
import random

app = FastAPI()

# In-memory store. Will move to Redis once the cluster has a backing service.
store: dict[str, str] = {}


class ShortUrlRequest(BaseModel):
    url:str

def generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/shorten", response_model=dict[str, str])
def shortenRequest(request: ShortUrlRequest)->dict[str, str]:
    code = generate_code()

    while code in store:
        code = generate_code()
    
    store[code] = request.url
    return {"code":code, "url":request.url}

@app.get("/healthz",response_model=dict[str,str])
def healthz():
    return {"status":"OK"}


@app.get("/r/{code}",response_model=dict[str,str])
def resolve(code: str):
    if code not in store:
        raise HTTPException(status_code=404, detail="code not found")
    return {"code":code,"url":store[code]}






