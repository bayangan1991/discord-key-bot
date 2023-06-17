from datetime import datetime

from discord.ext import commands

from discord_key_bot.colours import Colours
from discord_key_bot.db import Session
from discord_key_bot.db.models import Member
from discord_key_bot.keyparse import keyspace, parse_name
from discord_key_bot.utils import claimable, embed, find_games


class GuildCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def search(self, ctx, *game_name):
        """Searches available games"""

        msg = embed("Top 15 search results...", title="Search Results")

        session = Session()

        search_args = parse_name("_".join(game_name))

        games, _ = find_games(session, search_args, ctx.guild.id)

        for g, platforms in games.items():
            value = "\n".join(f"{p.title()}: {len(c)}" for p, c in platforms.items())
            msg.add_field(name=g, value=value, inline=True)

        await ctx.send(embed=msg)

    @commands.command()
    async def browse(self, ctx, page=1):
        """Browse through available games"""

        if not ctx.guild:
            await ctx.send(
                embed=embed(
                    "This command should be sent in a guild. To see your keys use `!mykeys`"
                )
            )

        session = Session()

        per_page = 20
        offset = (page - 1) * per_page

        games, query = find_games(session, "", ctx.guild.id, per_page, offset)

        first = offset + 1
        total = query.count()
        last = min(page * per_page, total)

        msg = embed(f"Showing {first} to {last} of {total}", title="Browse Games")

        for g in query.from_self().limit(per_page).offset(offset).all():
            msg.add_field(
                name=g.pretty_name, value=", ".join(k.platform.title() for k in g.keys)
            )

        await ctx.send(embed=msg)

    @commands.command()
    async def share(self, ctx):
        """Add this guild the guilds you share keys with"""
        session = Session()

        member = Member.get(session, ctx.author.id, ctx.author.name)

        if ctx.guild:
            if ctx.guild.id in member.guilds:
                await ctx.send(
                    embed=embed(
                        f"You are already sharing with {ctx.guild.name}",
                        colour=Colours.GOLD,
                    )
                )
            else:
                member.guilds.append(ctx.guild.id)
                session.commit()
                await ctx.send(
                    embed=embed(
                        f"Thanks {ctx.author.name}! Your keys are now available on {ctx.guild.name}",
                        colour=Colours.GREEN,
                    )
                )
        else:
            await ctx.send(
                embed=embed(
                    "You need to run this command in a guild. Not in a direct message",
                    colour=Colours.GOLD,
                )
            )

    @commands.command()
    async def unshare(self, ctx):
        """Remove this guild from the guilds you share keys with"""
        session = Session()
        member = Member.get(session, ctx.author.id, ctx.author.name)

        if ctx.guild:
            if ctx.guild.id not in member.guilds:
                await ctx.send(
                    embed=embed(
                        f"You aren't currently sharing with {ctx.guild.name}",
                        colour=Colours.GOLD,
                    )
                )
            else:
                member.guilds.remove(ctx.guild.id)
                session.commit()
                await ctx.send(
                    embed=embed(
                        f"Thanks {ctx.author.name}! You have removed {ctx.guild.name} from sharing",
                        colour=Colours.GREEN,
                    )
                )
        else:
            await ctx.send(
                embed=embed(
                    "You need to run this command in a guild. Not in a direct message",
                    colour=Colours.RED,
                )
            )

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
            return

        games, _ = find_games(session, search_args, ctx.guild.id, 3)

        if len(games.keys()) > 1:
            msg = embed(
                "Please limit your search",
                title="Too many games found",
                colour=Colours.RED,
            )

            for g, platforms in games.items():
                msg.add_field(name=g, value=", ".join(platforms.keys()))

            await ctx.send(embed=msg)
            return

        if not games:
            await ctx.send(embed=embed("Game not found"))
            return

        game_name = list(games.keys())[0]
        key = games[game_name][platform][0]
        game = key.game

        msg = embed(
            "Please find your key below", title="Game claimed!", colour=Colours.GREEN
        )

        msg.add_field(name=game.pretty_name, value=key.key)

        session.delete(key)
        session.commit()

        if not game.keys:
            session.delete(game)

        if key.creator_id != member.id:
            member.last_claim = datetime.utcnow()
        session.commit()

        await ctx.author.send(embed=msg)
        await ctx.send(
            embed=embed(
                f'"{game.pretty_name}" claimed by {ctx.user.name}. Check your PMs for more info. Enjoy!'
            )
        )
