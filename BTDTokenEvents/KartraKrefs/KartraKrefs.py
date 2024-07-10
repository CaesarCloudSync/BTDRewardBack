
import os
from dotenv import load_dotenv
load_dotenv(".env")
class KartraKrefs:
    def __init__(self):
        # Auth Krefs
        self.KREF_DAILY_TOKENS = os.getenv("KREF_DAILY_TOKENS")
        self.KREF_AUTHENTICATION = os.getenv("KREF_AUTHENTICATION")
        # BTD Token Shop Items
        self.KREF_SHOP_TEST_ITEM_1 = os.getenv("KREF_SHOP_TEST_ITEM_1")
        self.KREF_SHOP_TEST_ITEM_2 = os.getenv("KREF_SHOP_TEST_ITEM_2")
        # BTD Token Shop Item 


    def get_krefs(self):
        KREFS = [self.KREF_DAILY_TOKENS,self.KREF_AUTHENTICATION,self.KREF_SHOP_TEST_ITEM_1,self.KREF_SHOP_TEST_ITEM_2]
        return KREFS
    def get_shop_items(self):
        SHOP_KREFS = [self.KREF_SHOP_TEST_ITEM_1,self.KREF_SHOP_TEST_ITEM_2]
        return SHOP_KREFS
    def get_shop_item_price(self,shop_item):
        return os.getenv(f"{shop_item}_PRICE_TOKEN")