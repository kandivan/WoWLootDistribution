from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

from enum import Enum

Base = declarative_base()
    
class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_name = Column(String(300))
    in_game_name = Column(String(300))
    character_class = Column(String(300))
    raid_sim_settings = Column(JSON())
    raid_sim_results = Column(JSON())
    creation_date = Column(DateTime(), default = func.now())
    last_update = Column(DateTime(), default = func.now())

class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key = True)
    in_game_id = Column(Integer)
    name = Column(String(300))
    ilvl = Column(Integer)

class User(Base, UserMixin):
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    email = Column(String(200), unique=True)
    password = Column(String(1000)) # This is a salty pass
    
    @property
    def is_active(self):
        return True
    def set_password(self, bcrypt: Bcrypt, password: str):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, bcrypt: Bcrypt, password: str):
        return bcrypt.check_password_hash(self.password, password)
class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///wowlootdistribution.db')
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()
    def get_player_by_id(self, player_id):
        session = self.get_session()
        player = session.query(Player).filter_by(id=player_id).first()
        session.close()
        return player

    def get_players_by_discord_name(self, discord_name):
        session = self.get_session()
        players = session.query(Player).filter_by(discord_name=discord_name).all()
        session.close()
        return players

    def set_player_discord_name(self, player_id, new_discord_name):
        session = self.get_session()
        player = session.query(Player).filter_by(id=player_id).first()
        if player:
            player.discord_name = new_discord_name
            session.commit()
        session.close()

    # --- Item methods ---

    def get_item_by_id(self, item_id):
        session = self.get_session()
        item = session.query(Item).filter_by(id=item_id).first()
        session.close()
        return item

    def set_item_name(self, item_id, new_name):
        session = self.get_session()
        item = session.query(Item).filter_by(id=item_id).first()
        if item:
            item.name = new_name
            session.commit()
        session.close()

    # --- User methods ---

    def get_user_by_username(self, username):
        session = self.get_session()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        return user

    def set_user_email(self, user_id, new_email):
        session = self.get_session()
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.email = new_email
            session.commit()
        session.close()

