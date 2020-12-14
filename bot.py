import os
import random
import yfinance as yf
from dotenv import load_dotenv
import discord

# 1
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():

    print(f'{bot.user.name} has connected to Discord!')

    tsla_df = yf.download("MSFT", period="1d")
    # print(tsla_df.head(1))
    msg = '''\
        TSLA EOD Data
        - Open: {Open}
        - High: {High}
        - Low: {Low}
        - Close: {Close}
        - Adj Close: {Adj_Close}
        - Volume: {Volume}\
     '''.format(Open=tsla_df.iat[0, 0], High=tsla_df.iat[0, 1], Low=tsla_df.iat[0, 2], Close=tsla_df.iat[0, 3], Adj_Close=tsla_df.iat[0, 4], Volume=tsla_df.iat[0, 5])

    existing_channel = discord.utils.get(
        bot.guilds[0].channels, name='test-channel')

    await existing_channel.send(msg)


@bot.command(name="99", help='Responds with a random quote from Brooklyn 99.')
async def nine_nine(ctx):

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        'Cool dude!'
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

    # to send dm to the message author by the bot...
    # await ctx.message.author.send(response)


@bot.command(name="roll_dice", help="Simulates a rolling dice.")
async def roll(ctx, number_of_dice: int, number_of_sides: int):

    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]

    await ctx.send(', '.join(dice))


@bot.command(name="create-channel", help="An admin creates a new channel.")
@commands.has_role('admin')
async def create_channel(ctx, channel_name='test-channel'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)

    if not existing_channel:
        print(f'Creating a new channel- "{channel_name}"...')
        await guild.create_text_channel(channel_name)
        print('Channel created!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)