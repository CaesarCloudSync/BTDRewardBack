
from CaesarAIRedis.CaesarAIRedis import CaesarAIRedis


class BTDRedis(CaesarAIRedis):
    def __init__(self) -> None:
        super().__init__()
    def set_space(self,key,value):
        self.r.set(f"space:{key}",value)
    def get_space(self,key):
        return self.r.get(f"space:{key}")
    def delete_space(self,key):
        self.r.delete(f"space:{key}")
    def get_all_spaces(self,batch:str=500):
        # in batches of 500 delete keys matching user:*
        for keybatch in self.batcher(self.r.scan_iter('space:*'),batch):
            for key in keybatch:
                if key:
                    yield {key:self.r.get(key)}
    def set_conference(self,key,value):
        self.r.set(f"conference:{key}",value)
    def get_conference(self,key):
        return self.r.get(f"conference:{key}")
    def delete_conference(self,key):
        self.r.delete(f"conference:{key}")
    def get_all_conference(self,batch:str=500):
        # in batches of 500 delete keys matching user:*
        for keybatch in self.batcher(self.r.scan_iter('conference:*'),batch):
            for key in keybatch:
                if key:
                    yield {key:self.r.get(key)}
    def set_participant_session(self,key,value):
        self.r.set(f"participant-session:{key}",value)
    def get_participant_session(self,key):
        return self.r.get(f"participant-session:{key}")
    def delete_participant_session(self,key):
        self.r.delete(f"participant-session:{key}")
    def get_all_participant_session(self,batch:str=500):
        # in batches of 500 delete keys matching user:*
        for keybatch in self.batcher(self.r.scan_iter('participant-session:*'),batch):
            for key in keybatch:
                if key:
                    yield {key:self.r.get(key)}
