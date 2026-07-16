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
    score: float
    member: str

app = FastAPI(root_path="/redis")
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

@app.post("/incr/{key}")
def incr_value(key: str):
    try:
        result = db.incr(key)
        return {"key": key, "value": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

### Hashmap'e ait endpointler

@app.post("/hset")
def hset_value(request: HSetRequest):
    try:
        result = db.hset(request.key, request.field, request.value)
        return {"status": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/hget/{key}/{field}")
def hget_value(key: str, field: str):
    try:
        result = db.hget(key, field)
        return {"key": key, "field": field, "value": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
@app.get("/hgetall/{key}")
def hgetall_value(key:str):
    try:
        result = db.hgetall(key)
        return result
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/hdel/{key}/{field}")
def hdel_value(key: str, field: str):
    try:
        result = db.hdel(key, field)
        return {"status": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

### Sorted Set'e ait endpointler

@app.post("/zadd")
def zadd_value(request: ZAddRequest):
    try:
        result = db.zadd(request.key, request.score, request.member)
        return {"status": result}
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/zscore/{key}/{member}")
def zscore_value(key: str, member: str):
    try:
        result = db.zscore(key, member)
        return {"key": key, "member": member, "score": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/zrem/{key}/{member}")
def zrem_value(key: str, member: str):
    try:
        result = db.zrem(key, member)
        return {"status": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/zrange/{key}")
def zrange_value(key: str, start: int = 0, stop: int = -1):
    try:
        result = db.zrange(key, start, stop)
        return {"key": key, "members": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))