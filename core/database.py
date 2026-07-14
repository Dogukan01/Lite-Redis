from core.datatypes import RedisString, RedisHash, RedisSortedSet

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