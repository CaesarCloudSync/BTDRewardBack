
from .CaesarAIRedis import CaesarAIRedis


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
