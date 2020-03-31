"""Dynmap plugin.

Grabs data from a Minecraft server's dynmap to display how many players are
online in the bot's status message and through commands.
"""

from discord.ext import commands, tasks
import discord
from logzero import logger
from util import text_bar
import requests
import json
import config
import urllib.parse


def get_api_url(route):
    """Get a full URL from a route.

    Args:
        route (str): Route to the API endpoint (e.g. '/up/world/world/').

    Returns:
        str: The full URL that a request can be made to.
    """
    return urllib.parse.urljoin(config.get_value("DYNMAP_URL"), route)


def get_map_data():
    """Collect map data from the server's main world.

    Returns:
        dict: A dictionary of map data.
    """
    logger.debug("Collecting map data...")
    r = requests.get(get_api_url("/up/world/world/"))
    data = r.json()
    return data


class Dynmap(commands.Cog, name="Minecraft"):
    """A cog for discord.py containing Dynmap specific commands and events."""

    def __init__(self, bot):
        """Create an instance of the cog."""
        self.bot = bot
        self.data = None

        # Start the status refresh timer
        self.update_bot_status.start()

    def cog_unload(self):
        """Clean up before unloading the cog."""
        # Stop the status refresh timer
        self.update_bot_status.cancel()

    @tasks.loop(seconds=30)
    async def update_bot_status(self):
        """Function to update the bot's status every 30 seconds."""
        logger.debug("Updating bot status...")
        self.data = get_map_data()

        status_msg = "{} players online!".format(self.data["currentcount"])
        logger.debug("Setting status message to '{}'...".format(status_msg))

        # Set the bot's status to the new message
        activity = discord.Game(name=status_msg)
        await self.bot.change_presence(status=discord.Status.online,
                                       activity=activity)

    @update_bot_status.before_loop
    async def before_update_bot_status(self):
        """Function that is run before the status refresh timer is started."""
        logger.debug("Waiting for bot ready...")
        # Wait until the bot has started itself up before starting the status
        # refresh timer.
        await self.bot.wait_until_ready()

    @commands.command(aliases=["players"],
                      help=("Get a list of the players that are currently "
                            "online the Minecraft server."))
    async def online(self, ctx):
        """Command for getting a list of online players."""
        # If no data has been collected by the status refresh timer
        if self.data is None:
            await ctx.send(("There's no data! Please resend the command in a "
                            "few seconds!"))
            return

        message = ""

        # Show a different message if there are no players online
        if self.data["currentcount"] <= 0:
            message = "There are currently no players online"
        else:
            message = "There are currently {} players online:".format(
                    self.data["currentcount"])

            # Add a new line for each player
            for player in self.data["players"]:
                message += "\n  •  **`{}`**".format(player["name"])

        await ctx.send(message)

    @commands.command(help=("Get information about a specific player that is "
                            "online the Minecraft server."))
    async def player(self, ctx, username: str):
        """Command for getting information about a specific player."""
        # Find the player in the list of players, or get None
        player = next((p for p in self.data["players"] if
                      (p["name"].lower() == username.lower())), None)

        # If no player was found
        if player is None:
            await ctx.send("**`{}`** is not currently online!".format(username
                                                                      ))
            return

        print(player)

        # Create a new discord.py embed object with the player's information
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

        # Send the embed
        await ctx.send(embed=player_embed)

    @commands.command(help="Send a message to the Minecraft server.")
    async def send(self, ctx, *message):
        """Command for sending a message to the dynmap."""
        # The message argument is a list of strings. They need to be combined
        # into a single message
        msg = " ".join(message)

        # If the message is empty, skip
        if msg.strip() == "":
            return

        # Send the message to the dynmap
        logger.debug("Sending message '{}'...".format(msg))
        requests.post(get_api_url("/up/sendmessage"),
                      data=json.dumps({
                            "name": ctx.message.author.name,
                            "message": msg
                      }))


def setup(bot):
    """Install the cog to the bot."""
    bot.add_cog(Dynmap(bot))
