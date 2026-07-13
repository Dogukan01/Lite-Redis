from core.database import RedisDB
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class SetRequest(BaseModel):
    key: str
    value: str

class HSetRequest(BaseModel):
    key: str
    field: str
    value: str

class ZAddRequest(BaseModel):
    key: str
    score: str
    member: str

app = FastAPI()
db = RedisDB()

@app.post("/set")
def set_value(request: SetRequest):
    result = db.set(request.key, request.value)
    return {"status": result}

@app.get("/get/{key}")
def get_value(key: str):
    try:
        result = db.get(key)
        return {"key": key, "value": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.post("/hset")
# def hset_value(request: HSetRequest):
#     result = db.hset(request.key, request.field, request.value)
