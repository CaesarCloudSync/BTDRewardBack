from pydantic import BaseModel
class PurchaseShopItemModel(BaseModel):
    shop_item_kref:str
    price:str
    path:str