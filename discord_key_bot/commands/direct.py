from datetime import datetime, timedelta, timezone

from discord import Forbidden
from discord.ext import commands
from discord.ext.commands import Context

from discord_key_bot.colours import Colours
from discord_key_bot.db import Session
from discord_key_bot.db.models import Game, Key, Member
from discord_key_bot.keyparse import keyspace, parse_key, parse_name
from discord_key_bot.utils import embed

UTC = timezone(timedelta(hours=0))


class DirectCommands(commands.Cog):
    """Run these commands in private messages to the bot"""

    @commands.command()
    async def add(self, ctx: Context, key, *game_name):
        """Add a key or url"""
        session = Session()

        if ctx.guild:
            try:
                await ctx.message.delete()
            except Forbidden:
                await ctx.send(
                    "You should probably delete that message as everyone in here can see it. I would do it but I "
                    "don't have permission."
                )
            await ctx.author.send(
                embed=embed(
                    "You should really do this here, so it's only the bot giving away keys.",
                    colour=Colours.LUMINOUS_VIVID_PINK,
                )
            )

        if not game_name:
            await ctx.send(
                embed=embed(
                    "Game name is required!",
                    Colours.RED,
                )
            )
            return

        platform, key = parse_key(key)

        if not platform:
            await ctx.send(embed=embed(key, Colours.RED))
            return

        game = Game.get(session, " ".join(game_name))

        found = session.query(Key).filter(Key.key == key).count()

        if found:
            await ctx.send(
                embed=embed(
                    "Key already exists!",
                    Colours.GOLD,
                )
            )
            return

        member = Member.get(session, ctx.author.id, ctx.author.name)

        game.keys.append(Key(platform=platform, key=key, creator=member, game=game))

        session.commit()

        await ctx.author.send(
            embed=embed(
                f'Key for "{game.pretty_name}" added. Thanks {ctx.author.name}!',
                Colours.GREEN,
                title=f"{platform.title()} Key Added",
            )
        )

    @commands.command()
    async def remove(self, ctx, platform, *game_name):
        """Remove a key or url and send to you in a PM"""

        if platform not in keyspace.keys():
            await ctx.send(
                embed=embed(
                    f'"{platform}" is not valid platform',
                    colour=Colours.RED,
                    title="Search Error",
                )
            )
            return

        search_args = parse_name("_".join(game_name))

        if not search_args:
            await ctx.send(embed=embed("No game search provided!"))
            return

        session = Session()

        member = Member.get(session, ctx.author.id, ctx.author.name)

        query = (
            session.query(Game)
            .join(Key)
            .filter(
                Game.pretty_name.like(f"%{search_args}%"),
                Key.platform == platform,
                Key.creator_id == member.id,
            )
        )

        if query.count() > 1:
            msg = embed(
                "Please limit your search",
                title="Too many games found",
                colour=Colours.RED,
            )

            for g, platforms in query.items():
                msg.add_field(name=g, value=", ".join(platforms.keys()))

            await ctx.send(embed=msg)
            return

        if not query.count():
            await ctx.send(embed=embed("Game not found"))
            return

        game = query.first()
        key = (
            session.query(Key)
            .filter(Key.game == game, Key.creator_id == member.id)
            .first()
        )

        msg = embed(
            "Please find your key below", title="Key removed!", colour=Colours.GREEN
        )

        msg.add_field(name=game.pretty_name, value=key.key)

        session.delete(key)
        session.commit()

        if not game.keys:
            session.delete(game)

        if key.creator_id != member.id:
            member.last_claim = datetime.now(tz=UTC)
        session.commit()

        await ctx.author.send(embed=msg)

    @commands.command()
    async def mykeys(self, ctx, page=1):
        """Browse your own keys"""
        if ctx.guild:
            await ctx.author.send(
                embed=embed("This command needs to be sent in a direct message")
            )
            return

        session = Session()
        member = Member.get(session, ctx.author.id, ctx.author.name)

        per_page = 15
        offset = (page - 1) * per_page

        query = (
            session.query(Key)
            .join(Game)
            .filter(Key.creator_id == member.id)
            .order_by(Game.pretty_name.asc(), Key.platform.asc())
        )

        first = offset + 1
        total = query.count()
        last = min(page * per_page, total)

        msg = embed(f"Showing {first} to {last} of {total}")

        for k in query.limit(per_page).offset(offset).all():
            msg.add_field(name=f"{k.game.pretty_name}", value=f"{k.platform.title()}")

        await ctx.send(embed=msg)
