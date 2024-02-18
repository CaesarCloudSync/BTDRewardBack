
from .CaesarAIRedis import CaesarAIRedis

from BTDCalendar.BTDCalendarModel import SpaceRedisMappingModel
class BTDRedis(CaesarAIRedis):
    def __init__(self) -> None:
        super().__init__()
    def set_space(self,key,value):
        mapping = SpaceRedisMappingModel.model_validate(value)
        mapping = dict(mapping)
        finalvalue = ""
        for value in mapping.values():
            finalvalue += f"{str(value)}|"
        self.r.set(f"space:{key}",finalvalue)
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
