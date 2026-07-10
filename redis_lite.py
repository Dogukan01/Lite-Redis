class RedisLite:
    def __init__(self):
        # Global sözlük (key-value deposu)
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
        
        # Anahtar yoksa None döner (Redis'teki (nil) karşılığı)
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
