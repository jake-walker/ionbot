"""The bot."""

from discord.ext import commands
import os
from logzero import logger
import config

bot = commands.Bot(command_prefix="-")


@bot.event
async def on_ready():
    """Function when the bot is ready."""
    logger.info("Logged in as {0.user}!".format(bot))


def main():
    """Function for starting the bot."""
    logger.info("Starting IonBot!")

    config.check_required()

    count = 0
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            count += 1
            bot.load_extension("cogs.{}".format(file[:-3]))

    logger.info("Loaded {} cog(s)".format(count))

    bot.run(config.get_value("token"))


if __name__ == "__main__":
    main()
