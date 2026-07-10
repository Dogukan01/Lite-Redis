class RedisLite:
    def __init__(self):
        self.db = {}

    def set(self, key: str, value) -> str:
        """Belirtilen anahtara bir değer atar."""
        if not isinstance(key, str):
            raise TypeError("Anahtar (key) bir string olmalıdır.")
        if not isinstance(value, (str, int, float)):
            raise TypeError("Değer (value) string, int veya float olmalıdır.")
        
        self.db[key] = value
        return "OK"

    def get(self, key: str):
        """Belirtilen anahtarın değerini döndürür."""
        if not isinstance(key, str):
            raise TypeError("Anahtar (key) bir string olmalıdır.")
        
        return self.db.get(key)

    def delete(self, key: str) -> int:
        """Belirtilen anahtarı ve değerini siler. Silinen eleman sayısını (0 veya 1) döndürür."""
        if not isinstance(key, str):
            raise TypeError("Anahtar (key) bir string olmalıdır.")
        
        if key in self.db:
            del self.db[key]
            return 1
        return 0

    def incr(self, key: str) -> int:
        """Eğer değer sayıysa (int) 1 artırır. Anahtar yoksa 0 varsayıp 1 yapar."""
        if not isinstance(key, str):
            raise TypeError("Anahtar (key) bir string olmalıdır.")
        
        if key not in self.db:
            self.db[key] = 1
            return 1
        
        value = self.db[key]
        if not isinstance(value, int):
            raise TypeError("HATA: Anahtara ait değer bir tam sayı (integer) değil.")
        
        self.db[key] = value + 1
        return self.db[key]

    # --- Hashmap Metodları ---

    def hset(self, key: str, field: str, value) -> int:
        """Hash içinde belirtilen alana (field) değer atar. Yeni alan eklendiyse 1, güncellendiyse 0 döner."""
        if not isinstance(key, str) or not isinstance(field, str):
            raise TypeError("Anahtar (key) ve alan (field) string olmalıdır.")
        if not isinstance(value, (str, int, float)):
            raise TypeError("Değer (value) string, int veya float olmalıdır.")
        
        if key not in self.db:
            self.db[key] = {}
        elif not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) bir Hash tipinde değil.")
        
        is_new = 1 if field not in self.db[key] else 0
        self.db[key][field] = value
        return is_new

    def hget(self, key: str, field: str):
        """Hash içindeki belirtilen alanın değerini döndürür."""
        if not isinstance(key, str) or not isinstance(field, str):
            raise TypeError("Anahtar (key) ve alan (field) string olmalıdır.")
        
        if key not in self.db:
            return None
        if not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) bir Hash tipinde değil.")
        
        return self.db[key].get(field)

    def hdel(self, key: str, field: str) -> int:
        """Hash içindeki belirtilen alanı siler. Silindiyse 1, yoksa 0 döner."""
        if not isinstance(key, str) or not isinstance(field, str):
            raise TypeError("Anahtar (key) ve alan (field) string olmalıdır.")
        
        if key not in self.db:
            return 0
        if not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) bir Hash tipinde değil.")
        
        if field in self.db[key]:
            del self.db[key][field]
            return 1
        return 0

    def hgetall(self, key: str) -> dict:
        """Hash içindeki tüm alanları ve değerlerini döndürür."""
        if not isinstance(key, str):
            raise TypeError("Anahtar (key) bir string olmalıdır.")
        
        if key not in self.db:
            return {}
        if not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) bir Hash tipinde değil.")
        
        # Referans sızıntısını önlemek için bir kopya dönüyoruz
        return self.db[key].copy()

    # --- Sorted Set Metodları ---

    def zadd(self, key: str, score, member: str) -> int:
        """Sorted Set'e bir eleman ve skorunu ekler. Yeni eleman eklendiyse 1, skoru güncellendiyse 0 döner."""
        if not isinstance(key, str) or not isinstance(member, str):
            raise TypeError("Anahtar (key) ve üye (member) string olmalıdır.")
        if not isinstance(score, (int, float)):
            raise TypeError("Skor (score) bir sayı (int veya float) olmalıdır.")
        
        score = float(score)
        
        if key not in self.db:
            self.db[key] = {}
        elif not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) uygun tipte değil.")
        
        is_new = 1 if member not in self.db[key] else 0
        self.db[key][member] = score
        return is_new

    def zscore(self, key: str, member: str):
        """Sorted Set içindeki üyenin skorunu döndürür."""
        if not isinstance(key, str) or not isinstance(member, str):
            raise TypeError("Anahtar (key) ve üye (member) string olmalıdır.")
        
        if key not in self.db:
            return None
        if not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) uygun tipte değil.")
        
        return self.db[key].get(member)

    def zrem(self, key: str, member: str) -> int:
        """Sorted Set içinden bir üyeyi siler. Silindiyse 1, yoksa 0 döner."""
        if not isinstance(key, str) or not isinstance(member, str):
            raise TypeError("Anahtar (key) ve üye (member) string olmalıdır.")
        
        if key not in self.db:
            return 0
        if not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) uygun tipte değil.")
        
        if member in self.db[key]:
            del self.db[key][member]
            return 1
        return 0

    def zrange(self, key: str, start: int, stop: int) -> list:
        """Skorlara göre artan sırada üyeleri döndürür (start ve stop indekslerine göre)."""
        if not isinstance(key, str):
            raise TypeError("Anahtar (key) bir string olmalıdır.")
        if not isinstance(start, int) or not isinstance(stop, int):
            raise TypeError("Start ve stop indeksleri integer olmalıdır.")
            
        if key not in self.db:
            return []
        if not isinstance(self.db[key], dict):
            raise TypeError("HATA: Belirtilen anahtar (key) uygun tipte değil.")
        
        # (member, score) çiftlerini önce skora, skoru aynıysa alfabetik olarak member'a göre sıralarız
        sorted_items = sorted(self.db[key].items(), key=lambda item: (item[1], item[0]))
        
        # Redis ZRANGE davranışına göre stop inclusive (dahil) olur. -1 sona kadar demek.
        if stop == -1:
            return [item[0] for item in sorted_items[start:]]
        else:
            return [item[0] for item in sorted_items[start:stop+1]]
