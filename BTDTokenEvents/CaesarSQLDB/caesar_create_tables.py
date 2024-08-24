from CaesarSQLDB.caesarcrud import CaesarCRUD
class CaesarCreateTables:
    def __init__(self) -> None:
        self.usersfields = ("email","password")
        self.usersleadfields = ("kartraid","first_name","last_name","email","btduuid","membership") # Unique constraint was added manually on supabase for "btduuid"
        self.rewardleadfields = ("email","reward")
        self.rewardleadlogfields = ("email","reward","action","actiondetailsb64")
        self.aliaslinksfields = ("email","alias","aliaslink","datewhenaliascreated")
        self.invitedfriendsfields = ("recommender_email","friend_email")
        self.pendingpurchasesfields = ("email","checksum","shopitemkref")
        self.purchaseactionlogsfields = ("email","shopitemkref","price","datetime")
        

    def create(self,caesarcrud: CaesarCRUD):
        caesarcrud.create_table("aliaslinkid",self.aliaslinksfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "aliaslinks")
        
        caesarcrud.create_table("aliaslinkid",self.invitedfriendsfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "invitedfriends")
        caesarcrud.create_table("userid",self.usersfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "users")
        caesarcrud.create_table("userleadid",self.usersleadfields,
        ("INT NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","TEXT NOT NULL","varchar(255)"),
        "userleads")
        caesarcrud.create_table("rewardleadid",self.rewardleadfields,
        ("TEXT NOT NULL","INT NOT NULL"),
        "rewardleads")
        caesarcrud.create_table("rewardleadactionid",self.rewardleadlogfields,
        ("TEXT NOT NULL","INT NOT NULL","varchar(255) NOT NULL","TEXT NOT NULL"),
        "rewardactionlogs")
        caesarcrud.create_table("pendingpurchasesid",self.pendingpurchasesfields,
        ("varchar(255) NOT NULL","TEXT NOT NULL","varchar(255) NOT NULL"),
        "pendingpurchases")
        caesarcrud.create_table("purchaseactionlogsid",self.purchaseactionlogsfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","INT NOT NULL","varchar(255) NOT NULL"),
        "purchaseactionlogs")

