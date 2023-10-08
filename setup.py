from datetime import datetime
from database import Database, Player, Item, User
from datetime import datetime
import json

# Assuming you've already defined the above classes and the Database class

# Step 1: Create the database and tables
db = Database()
db.create_tables()

# Step 2: Write to the database

with open("./StaticData/playerSims.json", "r") as infile:
    raid_sim_settings = json.load(infile)
with open("./StaticData/db.json", "r") as itemdbfile:
    item_db = json.load(itemdbfile)
# Create a new player
index = 0
session = db.get_session()
for simSetting in raid_sim_settings.get("simSettings"):
    player = Player(discord_name=f"Player_{index}",
    in_game_name=f"Player_{index}",
    character_class="",
    raid_sim_settings=simSetting,
    raid_sim_results = None,
    creation_date=datetime.now(),
    last_update=datetime.now())
    session.add(player)
    index += 1
for item in item_db.get("items"):
    _item = Item(**item)
    session.add(_item)
session.commit()
players = session.query(Player).all()
for player in players:
    print(player.__dict__)

items = session.query(Item).all()
for item in items:
    print(item.__dict__)
# Optional: Close the session after you're done
session.close()