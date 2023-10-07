from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

from enum import Enum

Base = declarative_base()
    
class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    discord_name = Column(String(300))
    in_game_name = Column(String(300))
    character_class = Column(String(300))
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

