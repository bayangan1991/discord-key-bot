import os
from collections import defaultdict
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from .db import Session
from .db.models import Game, Key, Member
from .keyparse import parse_key, keyspace, parse_name
from .colours import Colours

bot = commands.Bot(command_prefix=os.environ.get("BANG", "!"))

WAIT_TIME = timedelta(seconds=int(os.environ.get("WAIT_TIME", 86400)))


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


class KeyStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, key, *game_name):
        """Add a key (Do this in a private message)"""
        session = Session()

        game = Game.get(session, " ".join(game_name))

        platform, key = parse_key(key)

        if ctx.guild:
            await ctx.message.delete()

        if not platform:
            await ctx.send(embed=embed(key, Colours.RED))
            return

        found = session.query(Key).filter(Key.key == key).count()

        if found:
            await ctx.send(
                embed=embed(
                    f"Key already exists!",
                    Colours.GOLD,
                )
            )
            return

        member = Member.get(session, ctx.author.id, ctx.author.name)

        game.keys.append(Key(platform=platform, key=key, creator=member, game=game))

        session.commit()

        await ctx.send(
            embed=embed(
                f'Key for "{game.pretty_name}" added. Thanks {ctx.author.name}!',
                Colours.GREEN,
                title=f"{platform.title()} Key Added",
            )
        )

    @commands.command()
    async def search(self, ctx, *game_name):
        """Searches avaiable games"""

        msg = embed("Top 20 search results...", title="Search Results")

        session = Session()

        search_args = parse_name("_".join(game_name))

        for g in (
            session.query(Game)
            .filter(Game.name.like(f"%{search_args}%"))
            .limit(20)
            .all()
        ):
            platforms = defaultdict(int)
            for k in g.keys:
                platforms[k.platform] += 1

            value = "\n".join(f"{p.title()}: {c}" for p, c in platforms.items())
            msg.add_field(name=g.pretty_name, value=value, inline=False)

        await ctx.send(embed=msg)

    @commands.command()
    async def claim(self, ctx, platform=None, *game_name):
        """Claims a game from available keys"""
        session = Session()

        member = Member.get(session, ctx.author.id, ctx.author.name)
        ready, timeleft = claimable(member.last_claim)
        if not ready:
            await ctx.send(
                embed=embed(
                    f"You must wait {timeleft} until your next claim",
                    colour=Colours.RED,
                    title="Failed to claim",
                )
            )
            return

        if platform not in keyspace.keys():
            await ctx.send(
                embed=embed(
                    f'"{platform}" is not valid platform',
                    colour=Colours.RED,
                    title="Failed to claim",
                )
            )
            return

        search_args = parse_name("_".join(game_name))

        if not search_args:
            await ctx.send(embed=embed("No game search provided!"))

        q = session.query(Game).filter(Game.name.like(f"%{search_args}%")).limit(3)

        if q.count() > 1:
            msg = embed(
                "Please limit your search",
                title="Too many games found",
                colour=Colours.RED,
            )

            for g in q.all():
                msg.add_field(name=g.pretty_name, value=len(g.keys))

            await ctx.send(embed=msg)
            return

        game = q.first()

        if not game:
            await ctx.send(embed=embed("Game not found"))

        for k in game.keys:
            if k.platform == platform:
                key = k
                break

        msg = embed(
            f"Please find your key below", title="Game claimed!", colour=Colours.GREEN
        )

        msg.add_field(name=game.pretty_name, value=key.key)

        session.delete(key)
        session.commit()

        if not game.keys:
            session.delete(game)

        if key.creator != member:
            member.last_claim = datetime.utcnow()
        session.commit()

        await ctx.author.send(embed=msg)


bot.add_cog(KeyStore(bot))
