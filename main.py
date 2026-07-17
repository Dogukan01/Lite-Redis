from core.database import RedisDB
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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

def nightly_backup_job():
    """Her gece saat 03:00'te tetiklenecek ana cron fonksiyonu"""
    print(f"[CRON JOB] Gece yedekleme işlemi başladı. Saat: {datetime.now()}")
    
    # 1. Adım: O anki tarihi alıp dosya adı üretiyoruz
    today_str = datetime.now().strftime("%Y-%m-%d")
    cron_filename = f"redis_lite_{today_str}.rdb"
    
    # 2. Adım: Tarihli dosyayı diske yaz
    db.save_to_disk(filename=cron_filename)
    
    # 3. Adım: Aynı zamanda ana dump dosyasını da güncel tut ki load_from_disk doğrudan oradan okuyabilsin
    db.save_to_disk(filename="redis_lite_dump.rdb")
    
    # 4. Adım: 7 günden eski olan dosyaları arkada temizle
    db.cleanup_old_backups()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [AÇILIŞ] Konteyner başlarken diskteki veriyi RAM'e geri yükle
    db.load_from_disk()
    
    # Zamanlayıcıyı (Scheduler) kuruyoruz
    scheduler = BackgroundScheduler()
    
    # Cron kuralı: Her gün (day_of_week='*'), saat 03:00'te (hour=3, minute=0) tetikle
    trigger = CronTrigger(hour=3, minute=0, day_of_week='*')
    scheduler.add_job(nightly_backup_job, trigger=trigger, id="nightly_backup")
    
    # Zamanlayıcıyı arka planda asenkron olarak uykuya yatırıyoruz, saati gelince uyanacak
    scheduler.start()
    print("[SİSTEM] Gece 03:00 CronJob zamanlayıcısı başarıyla başlatıldı.")
    
    yield
    
    # [KAPANIŞ] Sunucu kapatılırken veriler kaybolmasın diye son bir yedek alıyoruz
    print("[SİSTEM] Sunucu kapatılıyor, kapanış yedeği alınıyor...")
    db.save_to_disk(filename="redis_lite_dump.rdb")
    scheduler.shutdown()

@app.post("/admin/backup")
async def trigger_manual_backup(background_tasks: BackgroundTasks):
    """
    Swagger UI üzerinden veya kod içinden manuel tetikleyebileceğin yedekleme endpoint'i.
    API'yi kilitlememesi için işlemi arka plan görevi olarak çalıştırır.
    """
    # Manuel yedek ismini saat ve dakika içererek üretiyoruz (Örn: redis_lite_manual_2026-07-17_18-45.rdb)
    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    manual_filename = f"redis_lite_manual_{now_str}.rdb"
    
    # API yanıtının hızlı dönmesi, diske yazma işleminin arkada sessizce akması için arka plana atıyoruz
    background_tasks.add_task(db.save_to_disk, manual_filename)
    background_tasks.add_task(db.save_to_disk, "redis_lite_dump.rdb") # Ana dump dosyasını da tazele
    
    return {
        "durum": "Yedekleme işlemi arka planda başlatıldı",
        "olusturulan_dosya": manual_filename,
        "mesaj": "Verileriniz güvenle diske kaydediliyor."
    }