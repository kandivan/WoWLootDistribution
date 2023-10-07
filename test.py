from datetime import datetime
from database import Database, Player, Item, User
from datetime import datetime

# Assuming you've already defined the above classes and the Database class

# Step 1: Create the database and tables
db = Database()
db.create_tables()

# Step 2: Write to the database

# Create a new player
# new_player = Player(
#     discord_name="JohnDoe#1234",
#     in_game_name="JohnDoe",
#     character_class="Warrior",
#     creation_date=datetime.now(),
#     last_update=datetime.now()
# )

# # Create a new item
# new_item = Item(
#     in_game_id=101,
#     name="Sword of Valor",
#     ilvl=50
# )

# Add the new player and item to the session and commit
session = db.get_session()
# session.add(new_player)
# session.add(new_item)
# session.commit()

# Optional: Close the session after you're done
# session.close()

players = session.query(User).all()
for player in players:
    print(player.email)