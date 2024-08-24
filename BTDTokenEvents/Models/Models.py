from pydantic import BaseModel
from typing import Optional
class PurchaseShopItemModel(BaseModel):
    shop_item_kref:str
    price:str
    path:str
