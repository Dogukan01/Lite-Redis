from collections import OrderedDict

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

# class RedisList:
#     def __init__(self, initial_value=None):
#         self.value = initial_value if initial_value is not None else []

#     def lpush(self, item):
#         self.value.insert(0, item)
#         return len(self.value)

#     def lrange(self):
#         return self.value.copy()

class RedisCompanyHistory:
    def __init__(self):
        self.visitors = {}

    def add_query(self, vid, query):
        if vid not in self.visitors:
            self.visitors[vid] = RedisMRU()

        return self.visitors[vid].add_query(query)

    def get_queries_by_vid(self, vid):
        if vid in self.visitors:
            return self.visitors[vid].get_query()
        return []

    def get_all(self):
        return {vid: mru.get_query() for vid, mru in self.visitors.items()}

        
class RedisMRU:
    def __init__(self):
        self.value = OrderedDict()
    
    def add_query(self, query):
        self.value[query] = None
        self.value.move_to_end(query, last=False)
        if len(self.value) > 20:
            self.value.popitem(last=True)
        return len(self.value)

    def get_query(self):
        return list(self.value.keys())

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
        try:
            score_float = float(score)
        except (ValueError, TypeError):
            raise ValueError("ERR value is not a valid float")
            
        is_new = member not in self.members
        self.members[member] = score_float

        if is_new:
            return 1
        else:
            return 0

    def zscore(self, member):
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

