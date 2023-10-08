from datetime import datetime
from database import Database, Player, Item, User
from datetime import datetime
import json

# Assuming you've already defined the above classes and the Database class

# Step 1: Create the database and tables
db = Database()
db.create_tables()

# Step 2: Write to the database

with open("input.json", "r") as infile:
    raid_sim_settings = json.load(infile)

with open("output.json", "r") as outfile:
    raid_sim_results = json.load(outfile)

with open("beachie_input.json", "r") as infile:
    beachie_raid_sim_settings = json.load(infile)
# Create a new player
new_player = Player(
    discord_name="KandiVan",
    in_game_name="Kandowo",
    character_class="Mage",
    raid_sim_settings=raid_sim_settings,
    raid_sim_results = raid_sim_results,
    creation_date=datetime.now(),
    last_update=datetime.now()
)
bestie = Player(discord_name="Bestie",
                in_game_name = "Bestie",
                character_class="Druid",
                raid_sim_settings = beachie_raid_sim_settings,
                raid_sim_results = raid_sim_results,
                creation_date = datetime.now(),
                last_update = datetime.now())
# Add the new player and item to the session and commit
session = db.get_session()
session.add(new_player)
session.add(bestie)
session.commit()



players = session.query(Player).all()
for player in players:
    print(player.__dict__)

# Optional: Close the session after you're done
session.close()