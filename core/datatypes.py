class RedisString:
    def __init__(self, value):
        self.value = value

    def incr(self):
        try:
            self.value = int(self.value)
        except (ValueError, TypeError):
            raise TypeError("Girilen değer integer olmalıdır veya integer formatına dönüştürülebilmelidir.")
       
        self.value += 1
        return self.value



class RedisHash:
    def __init__(self):
        self.fields = {}

    def hset(self, field, value):
        is_new = field not in self.fields
        self.fields[field] = value
        if is_new:
            return 1
        else:
            return 0

    def hget(self, field):
        if field in self.fields:
            return self.fields.get(field)

    def hdel(self, field):
        if field in self.fields:
            del self.fields[field]
            return 1
        return 0

    def hgetall(self):
        return self.fields.copy()



class RedisSortedSet:
    def __init__(self):
        self.members = {}

    def zadd(self, member, score):
        is_new = member not in self.members
        self.members[member] = float(score) #float dönüşümü valuerror fırlatabilir!!

        if is_new:
            return 1
        else:
            return 0
    def zscore(self, member):
        if member in self.members:
            return self.members.get(member)

    def zrem(self, member):
        if member in self.members:
            del self.members[member]
            return 1
        return 0

    def zrange(self, start, stop):
        sorted_items = sorted(self.members.items(), key=lambda item:(item[1], item[0]))
        names = [item[0] for item in sorted_items]
        if stop == -1:
            return names[start:]
        else:
            return names[start:stop+1]

