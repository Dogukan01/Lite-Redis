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
