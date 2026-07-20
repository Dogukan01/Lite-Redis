from core.datatypes import RedisString, RedisHash, RedisSortedSet, RedisList
import pickle
import os
import glob
from datetime import datetime, timedelta

DB_DIR = "/data/"
DEFAULT_FILE_PATH = os.path.join(DB_DIR, "redis_lite_dump.rdb")

class RedisDB:
    def __init__(self):
        self.storage = {}

    def set(self, key, value):
        self.storage[key] = RedisString(value)
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
            return self.storage[key].incr()
        else:
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")
            
    def hset(self, key, field, value):
        if key not in self.storage:
            self.storage[key] = RedisHash()
        elif not isinstance(self.storage[key], RedisHash):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")
        
        return self.storage[key].hset(field, value)

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

        return self.storage[key].hdel(field)

    def zadd(self, key, score, member):
        if key not in self.storage:
            self.storage[key] = RedisSortedSet()
        elif not isinstance(self.storage[key], RedisSortedSet):
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")

        return self.storage[key].zadd(member, score)

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

        return self.storage[key].zrem(member)

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
            # Klasör yoksa kodun patlamaması için her ihtimale karşı oluşturuyoruz
            os.makedirs(DB_DIR, exist_ok=True)
            
            # Eğer özel bir isim verilmediyse varsayılan rdb ismini kullan
            actual_filename = filename if filename else "redis_lite_dump.rdb"
            target_path = os.path.join(DB_DIR, actual_filename)
            temp_path = f"{target_path}.tmp"
            
            # Veriyi önce geçici (.tmp) dosyaya yazıyoruz (Yazma anında elektrik kesilirse ana yedek bozulmasın diye)
            with open(temp_path, "wb") as f:
                pickle.dump(self.storage, f)
            
            # Yazma işlemi başarıyla bitince geçici dosyanın adını asıl hedef adıyla değiştiriyoruz
            os.replace(temp_path, target_path)
            print(f"[YEDEK] Veritabanı başarıyla kaydedildi: {target_path}")
            return actual_filename
        except Exception as e:
            print(f"[HATA] Diske kaydetme işlemi başarısız: {e}")
            return None

    def load_from_disk(self):
        """Uygulama açılırken en güncel yedeği bulur ve belleğe yükler."""
        # İlk olarak ana güncel dosya var mı diye bakıyoruz
        if os.path.exists(DEFAULT_FILE_PATH):
            load_path = DEFAULT_FILE_PATH
        else:
            # Eğer ana dosya yoksa, klasördeki cron ile alınmış en güncel rdb dosyasını seçelim
            search_pattern = os.path.join(DB_DIR, "redis_lite_*.rdb")
            all_backups = glob.glob(search_pattern)
            if all_backups:
                # Dosyaları değiştirilme tarihine göre sıralayıp en güncelini alıyoruz
                load_path = max(all_backups, key=os.path.getmtime)
            else:
                print("[BAŞLANGIÇ] Disk üzerinde hiçbir yedek bulunamadı. Temiz bellek ile açılıyor.")
                return

        try:
            with open(load_path, "rb") as f:
                self.storage = pickle.load(f)
            print(f"[BAŞLANGIÇ] Veriler başarıyla diskten RAM'e yüklendi. Kaynak: {load_path}")
        except Exception as e:
            print(f"[HATA] Yedek dosyası okunurken hata oluştu: {e}")

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

        return self.storage[vid].lpush(query)

    def get_history(self, vid: str):
        if vid not in self.storage:
            return []
        if isinstance(self.storage[vid], RedisList):
            return self.storage[vid].lrange()
        else:
            raise TypeError("HATA (WRONGTYPE): Anahtar üzerinde geçersiz veri türü işlemi yapılmaya çalışıldı.")
