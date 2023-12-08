class CaesarCreateTables:
    def __init__(self) -> None:
        self.usersfields = ("email","password")
        self.usersleadfields = ("first_name","last_name","last_name2","email","address")
        self.rewardleadfields = ("email","reward")
        self.rewardleadlogfields = ("email","reward","action")

        

    def create(self,caesarcrud):
        caesarcrud.create_table("userid",self.usersfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "users")
        caesarcrud.create_table("userleadid",self.usersleadfields,
        ("varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL","varchar(255) NOT NULL"),
        "userleads")
        caesarcrud.create_table("rewardleadid",self.rewardleadfields,
        ("TEXT NOT NULL","INT NOT NULL"),
        "rewardleads")
        caesarcrud.create_table("rewardleadid",self.rewardleadlogfields,
        ("TEXT NOT NULL","INT NOT NULL","varchar(255) NOT NULL"),
        "rewardactionlogs")


