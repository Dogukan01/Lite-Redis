from core.datatypes import RedisString, RedisHash, RedisSortedSet, RedisList
from datetime import datetime, timedelta
import pickle
import os
import glob
import threading
import time

DB_DIR = "/data/"
DEFAULT_FILE_PATH = os.path.join(DB_DIR, "redis_lite_dump.rdb")

class RedisDB:
    def __init__(self):
        self.storage = {}
        os.makedirs(DB_DIR, exist_ok=True)
        self.aof_path = os.path.join(DB_DIR, "appendonly.aof")
        self.aof_file = open(self.aof_path, "a")
        self.is_replaying = False

        def _background_fsync_():
            while True:
                time.sleep(1)
                try:
                    if hasattr(self, 'aof_file') and not self.aof_file.closed:
                        self.aof_file.flush()
                        os.fsync(self.aof_file.fileno())
                except Exception:
                        pass

        threading.Thread(target=_background_fsync_, daemon=True).start()        

    def _log_to_aof(self, command, *args):
        if self.is_replaying:
            return
        try:
            line = f"{command} " + " ".join(str(arg) for arg in args) + "\n"
            self.aof_file.write(line)
            
        except Exception as e:
            print(f"[AOF HATA] AOF yazılamadı: {e}")

    def set(self, key, value):
        self.storage[key] = RedisString(value)
        self._log_to_aof("SET", key, value)
        return "OK"

    def get(self, key):
        if key in self.storage:
            if isinstance(self.storage[key], RedisString):
                return self.storage[key].value
            else:
                raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")
        else:
            return None

    def incr(self, key):
        if key not in self.storage:
            self.set(key,0)

        if isinstance(self.storage[key], RedisString):
            result = self.storage[key].incr()
            self._log_to_aof("INCR", key)
            return result
        else:
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")
            
    def hset(self, key, field, value):
        if key not in self.storage:
            self.storage[key] = RedisHash()
        elif not isinstance(self.storage[key], RedisHash):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")
        
        result = self.storage[key].hset(field, value)
        self._log_to_aof("HSET", key, field, value)
        return result

    def hgetall(self, key):
        if key not in self.storage:
            return {}
        if isinstance(self.storage[key], RedisHash):
            return self.storage[key].hgetall()
        else:
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

    def hget(self, key, field):
        if key not in self.storage:
            return None
        elif not isinstance(self.storage[key], RedisHash):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        return self.storage[key].hget(field)
        
    def hdel(self, key, field):
        if key not in self.storage:
            return 0
        elif not isinstance(self.storage[key], RedisHash):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        result = self.storage[key].hdel(field)
        if result > 0:
            self._log_to_aof("HDEL", key, field)
        return result

    def zadd(self, key, score, member):
        if key not in self.storage:
            self.storage[key] = RedisSortedSet()
        elif not isinstance(self.storage[key], RedisSortedSet):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        result = self.storage[key].zadd(member, score)
        self._log_to_aof("ZADD", key, score, member)
        return result

    def zscore(self, key, member):
        if key not in self.storage:
            return None
        elif not isinstance(self.storage[key], RedisSortedSet):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        return self.storage[key].zscore(member)

    def zrem(self, key, member):
        if key not in self.storage:
            return 0
        elif not isinstance(self.storage[key], RedisSortedSet):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        result = self.storage[key].zrem(member)
        if result > 0:
            self._log_to_aof("ZREM", key, member)
        return result

    def zrange(self, key, start, stop):
        if key not in self.storage:
            return []
        elif not isinstance(self.storage[key], RedisSortedSet):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        return self.storage[key].zrange(start, stop)

    def save_to_disk(self, filename=None):
        """
        Bellekteki veriyi diske yazar.
        filename verilirse (örn: redis_lite_2026-07-17.rdb) o isimle kaydeder.
        """
        try:
            os.makedirs(DB_DIR, exist_ok=True)
            actual_filename = filename if filename else "redis_lite_dump.rdb"
            target_path = os.path.join(DB_DIR, actual_filename)
            temp_path = f"{target_path}.tmp"
            
            with open(temp_path, "wb") as f:
                pickle.dump(self.storage, f)
            
            os.replace(temp_path, target_path)
            print(f"[YEDEK] Veritabanı başarıyla kaydedildi: {target_path}")
            return actual_filename
        except Exception as e:
            print(f"[HATA] Diske kaydetme işlemi başarısız: {e}")
            return None

    def bgsave(self, filename=None):
        """Arka planda (ayrı thread) RDB kaydı alır ve AOF'yi temizler (Log Rotation)."""
        print("[BGSAVE] Arka plan yedekleme (BGSAVE) başlatılıyor...")
        
        # 1. Snapshot for thread
        storage_snapshot = dict(self.storage)
        
        # 2. AOF Rotation
        if hasattr(self, 'aof_file') and not self.aof_file.closed:
            self.aof_file.close()
            
        old_aof_path = self.aof_path + ".old"
        if os.path.exists(self.aof_path):
            os.replace(self.aof_path, old_aof_path)
            
        # Open fresh AOF for ongoing traffic
        self.aof_file = open(self.aof_path, "a")
        
        def save_task(snapshot_data, old_aof):
            try:
                os.makedirs(DB_DIR, exist_ok=True)
                actual_filename = filename if filename else "redis_lite_dump.rdb"
                target_path = os.path.join(DB_DIR, actual_filename)
                temp_path = f"{target_path}.tmp"
                
                with open(temp_path, "wb") as f:
                    pickle.dump(snapshot_data, f)
                
                os.replace(temp_path, target_path)
                print(f"[BGSAVE] Veriler diske yazıldı: {target_path}")
                
                # Eğer özel bir isim verildiyse, asıl dump dosyasını da güncelleyelim ki sistem oradan okusun
                if actual_filename != "redis_lite_dump.rdb":
                    import shutil
                    dump_path = os.path.join(DB_DIR, "redis_lite_dump.rdb")
                    shutil.copy2(target_path, dump_path)
                
                if os.path.exists(old_aof):
                    os.remove(old_aof)
                    print(f"[BGSAVE] Eski AOF dosyası temizlendi.")
            except Exception as e:
                print(f"[BGSAVE HATA] İşlem başarısız: {e}")

        # Başlat
        t = threading.Thread(target=save_task, args=(storage_snapshot, old_aof_path))
        t.start()
        return "BGSAVE started in background"

    def load_from_disk(self):
        """Uygulama açılırken en güncel yedeği bulur ve belleğe yükler."""
        if os.path.exists(DEFAULT_FILE_PATH):
            load_path = DEFAULT_FILE_PATH
        else:
            search_pattern = os.path.join(DB_DIR, "redis_lite_*.rdb")
            all_backups = glob.glob(search_pattern)
            if all_backups:
                load_path = max(all_backups, key=os.path.getmtime)
            else:
                print("[BAŞLANGIÇ] Disk üzerinde RDB yedeği bulunamadı.")
                load_path = None

        if load_path:
            try:
                with open(load_path, "rb") as f:
                    self.storage = pickle.load(f)
                print(f"[BAŞLANGIÇ] RDB başarıyla yüklendi: {load_path}")
            except Exception as e:
                print(f"[HATA] RDB okunurken hata oluştu: {e}")
                
        # AOF Replay
        self._replay_aof()

    def _replay_aof(self):
        if not os.path.exists(self.aof_path):
            return
            
        print("[BAŞLANGIÇ] AOF dosyası okunuyor ve komutlar işleniyor...")
        self.is_replaying = True
        try:
            with open(self.aof_path, "r") as f:
                for line in f:
                    parts = line.strip().split(" ", 2)
                    if not parts:
                        continue
                        
                    cmd = parts[0].upper()
                    if cmd == "SET" and len(parts) >= 3:
                        self.set(parts[1], parts[2])
                    elif cmd == "INCR" and len(parts) >= 2:
                        self.incr(parts[1])
                    elif cmd == "HSET":
                        inner_parts = line.strip().split(" ", 3)
                        if len(inner_parts) >= 4:
                            self.hset(inner_parts[1], inner_parts[2], inner_parts[3])
                    elif cmd == "HDEL" and len(parts) >= 3:
                        self.hdel(parts[1], parts[2])
                    elif cmd == "ZADD":
                        inner_parts = line.strip().split(" ", 3)
                        if len(inner_parts) >= 4:
                            self.zadd(inner_parts[1], inner_parts[2], inner_parts[3])
                    elif cmd == "ZREM" and len(parts) >= 3:
                        self.zrem(parts[1], parts[2])
                    elif cmd == "SET_HISTORY":
                        inner_parts = line.strip().split(" ", 2)
                        if len(inner_parts) >= 3:
                            self.set_history(inner_parts[1], inner_parts[2])
        except Exception as e:
            print(f"[AOF HATA] Replay hatası: {e}")
        finally:
            self.is_replaying = False
            
        print("[BAŞLANGIÇ] AOF geri yükleme tamamlandı.")

    def cleanup_old_backups(self):
        """/data/ klasöründeki 7 günden daha eski yedek dosyalarını temizler."""
        try:
            # 7 gün öncesinin tarih sınırını hesapla
            time_threshold = datetime.now() - timedelta(days=7)
            
            # Klasör içindeki "redis_lite_*.rdb" şablonuna uyan tüm dosyaları bulur
            search_pattern = os.path.join(DB_DIR, "redis_lite_*.rdb")
            all_backup_files = glob.glob(search_pattern)
            
            for file_path in all_backup_files:
                # Varsayılan dump dosyasını (redis_lite_dump.rdb) asla silmiyoruz, o sistemin kalbi
                if "redis_lite_dump.rdb" in file_path:
                    continue
                    
                # Dosyanın son değiştirilme/oluşturulma zamanını alıyoruz
                file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Eğer dosya 7 günden eskiyse sistemden kalıcı olarak temizle
                if file_modified_time < time_threshold:
                    os.remove(file_path)
                    print(f"[TEMİZLİK] 7 günden eski yedek dosyası silindi: {file_path}")
        except Exception as e:
            print(f"[HATA] Eski yedekleri temizleme işlemi başarısız: {e}")

    def set_history(self, vid: str, query: str):
        if vid not in self.storage:
            self.storage[vid] = RedisList()
        elif not isinstance(self.storage[vid], RedisList):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        result = self.storage[vid].lpush(query)
        self._log_to_aof("SET_HISTORY", vid, query)
        return result

    def get_history(self, vid: str):
        if vid not in self.storage:
            return []
        if isinstance(self.storage[vid], RedisList):
            return self.storage[vid].lrange()
        else:
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")
