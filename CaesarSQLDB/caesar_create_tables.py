class CaesarCreateTables:
    def __init__(self) -> None:
        self.usersfields = ("email","password")
        self.usersleadfields = ("first_name","last_name","email")
        self.rewardleadfields = ("email","reward")
        self.rewardleadlogfields = ("email","reward","action")
        self.aliaslinksfields = ("email","alias","aliaslink","datewhenaliascreated")
        self.invitedfriendsfields = ("recommender_email","friend_email")

        

    def create(self,caesarcrud):
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
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "userleads")
        caesarcrud.create_table("rewardleadid",self.rewardleadfields,
        ("TEXT NOT NULL","INT NOT NULL"),
        "rewardleads")
        caesarcrud.create_table("rewardleadid",self.rewardleadlogfields,
        ("TEXT NOT NULL","INT NOT NULL","varchar(255) NOT NULL"),
        "rewardactionlogs")


