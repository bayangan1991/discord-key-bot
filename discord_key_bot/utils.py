import os
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import groupby

import discord

from discord_key_bot.colours import Colours
from discord_key_bot.db.models import Game, Guild, Key, Member


def claimable(timestamp):
    if timestamp:
        return (
            datetime.utcnow() - timestamp > WAIT_TIME,
            timestamp + WAIT_TIME - datetime.utcnow(),
        )
    else:
        return True, None


def embed(text, colour=Colours.DEFAULT, title="Keybot"):
    msg = discord.Embed(title=title, type="rich", description=text, color=colour)

    return msg


def find_games(session, search_args, guild_id, limit=15, offset=None):
    query = (
        session.query(Game)
        .join(Key)
        .filter(
            Key.creator_id.in_(
                session.query(Member.id).join(Guild).filter(Guild.guild_id == guild_id)
            )
        )
        .filter(Game.name.like(f"%{search_args}%"))
        .order_by(Game.pretty_name.asc())
    )

    if offset is None:
        games = defaultdict(lambda: defaultdict(list))

        for g in query.from_self().offset(offset).limit(limit).all():
            games[g.pretty_name] = {
                k: list(v) for k, v in groupby(g.keys, lambda x: x.platform)
            }
    else:
        games = None

    return games, query


WAIT_TIME = timedelta(seconds=int(os.environ.get("WAIT_TIME", 86400)))
