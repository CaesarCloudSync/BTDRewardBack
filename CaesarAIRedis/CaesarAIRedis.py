import redis
from itertools import zip_longest



class CaesarAIRedis:
    def __init__(self) -> None:
        self.r= redis.Redis(host='localhost', port=6379, decode_responses=True)

    def setkey(self,key:str,mapping:dict):
        self.r.hset(key,mapping=mapping)
    def getkey(self,key:str):
        return self.r.hgetall(key)
    def deletekey(self,key:str):
        self.r.delete(key)
    def setsession(self,trackingid:str,mapping:dict):
        self.r.hset(f"user-session:{trackingid}",mapping=mapping)
    def getsession(self,trackingid:str):
        return self.r.hgetall(f"user-session:{trackingid}")
    def deletesession(self,trackingid:str):
        self.r.delete(f"user-session:{trackingid}")
    def batcher(self,iterable, n):
        args = [iter(iterable)] * n
        return zip_longest(*args)

    def deleteallsessions(self):
        for key in self.r.scan_iter("user-session:*'"):
            self.r.delete(key)
            
    def streamallsessionids(self,batch:str=500):
        # in batches of 500 delete keys matching user:*
        for keybatch in self.batcher(self.r.scan_iter('user-session:*'),batch):
            for key in keybatch:
                if key:
                    yield key
    def streamallsessions(self,batch:str=500):
        # in batches of 500 delete keys matching user:*
        for keybatch in self.batcher(self.r.scan_iter('user-session:*'),batch):
            for key in keybatch:
                if key:
                    yield {key:self.r.hgetall(key)}
    def deletestreamallsessions(self,batch:str=500):
        # in batches of 500 delete keys matching user:*
        for keybatch in self.batcher(self.r.scan_iter('user-session:*'),batch):
            for key in keybatch:
                if key:
                    self.r.delete(key)
