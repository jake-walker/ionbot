from discord.ext import commands, tasks
import discord
from logzero import logger
from util import text_bar
import requests
import json
import config
import urllib.parse


def get_api_url(route):
    return urllib.parse.urljoin(config.get_value("DYNMAP_URL"), route)


def get_map_data():
    logger.debug("Collecting map data...")
    r = requests.get(get_api_url("/up/world/world/"))
    data = r.json()
    return data


class Dynmap(commands.Cog, name="Minecraft"):
    def __init__(self, bot):
        self.bot = bot
        self.data = None
        self.update_bot_status.start()

    def cog_unload(self):
        self.update_bot_status.cancel()

    @tasks.loop(seconds=30)
    async def update_bot_status(self):
        logger.debug("Updating bot status...")
        self.data = get_map_data()

        status_msg = "{} players online!".format(self.data["currentcount"])
        logger.debug("Setting status message to '{}'...".format(status_msg))

        activity = discord.Game(name=status_msg)
        await self.bot.change_presence(status=discord.Status.online,
                                       activity=activity)

    @update_bot_status.before_loop
    async def before_update_bot_status(self):
        logger.debug("Waiting for bot ready...")
        await self.bot.wait_until_ready()

    @commands.command(aliases=["players"],
                      help=("Get a list of the players that are currently "
                            "online the Minecraft server."))
    async def online(self, ctx):
        if self.data is None:
            await ctx.send(("There's no data! Please resend the command in a "
                            "few seconds!"))
            return

        message = ""

        if self.data["currentcount"] <= 0:
            message = "There are currently no players online"
        else:
            message = "There are currently {} players online:".format(
                    self.data["currentcount"])

            for player in self.data["players"]:
                message += "\n  •  **`{}`**".format(player["name"])

        await ctx.send(message)

    @commands.command(help=("Get information about a specific player that is "
                            "online the Minecraft server."))
    async def player(self, ctx, username: str):
        player = next((p for p in self.data["players"] if
                      (p["name"].lower() == username.lower())), None)

        if player is None:
            await ctx.send("**`{}`** is not currently online!".format(username
                                                                      ))
            return

        print(player)

        player_embed = discord.Embed(
            title="Player **`{}`**".format(player["name"]))
        player_embed.set_thumbnail(
            url="https://minotar.net/helm/{}/512.png".format(player["name"]))

        player_embed.add_field(name="Username", value=player["name"])
        player_embed.add_field(name="Current World", value=player["world"])
        player_embed.add_field(name="Health",
                               value=text_bar(int(player["health"]), 20),
                               inline=False)
        player_embed.add_field(name="Armor",
                               value=text_bar(int(player["armor"]), 20),
                               inline=False)
        player_embed.add_field(name="Location (XYZ)",
                               value="`{}` `{}` `{}`".format(
                                   int(player["x"]),
                                   int(player["y"]),
                                   int(player["z"])))

        await ctx.send(embed=player_embed)

    @commands.command(help="Send a message to the Minecraft server.")
    async def send(self, ctx, *message):
        msg = " ".join(message)

        if msg.strip() == "":
            return

        logger.debug("Sending message '{}'...".format(msg))
        requests.post(get_api_url("/up/sendmessage"),
                      data=json.dumps({
                            "name": ctx.message.author.name,
                            "message": msg
                      }))


def setup(bot):
    bot.add_cog(Dynmap(bot))
