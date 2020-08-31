import re
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

from discord_key_bot.keyparse import parse_name

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    pretty_name = Column(String)

    @classmethod
    def get(cls, session, pretty_name):
        name = parse_name(pretty_name)
        game = session.query(cls).filter(cls.name == name).first()

        if not game:
            game = cls(name=name, pretty_name=pretty_name)
            session.add(game)

        return game


class Key(Base):
    __tablename__ = "keys"

    id = Column(Integer, primary_key=True)
    key = Column(String)
    platform = Column(String)

    creator_id = Column(Integer, ForeignKey("members.id"))
    creator = relationship("Member", backref="keys")

    game_id = Column(Integer, ForeignKey("games.id"))
    game = relationship("Game", backref="keys")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    last_claim = Column(DateTime)

    _guilds = relationship("Guild", cascade="all, delete-orphan")
    guilds = association_proxy(
        "_guilds",
        "guild_id",
        creator=lambda id: Guild(guild_id=id),
        cascade_scalar_deletes=True,
    )

    @classmethod
    def get(cls, session, id, name):
        member = session.query(cls).filter(cls.id == id).first()

        if not member:
            member = cls(id=id, name=name)
            session.add(member)

        return member


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer)
    member_id = Column(Integer, ForeignKey("members.id"))
