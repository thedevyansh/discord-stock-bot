import os
import random
import yfinance as yf
from dotenv import load_dotenv
import discord

import aiocron

# 1
from discord.ext import commands

top_stock_companies = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'FB', 'BRK-B', 'SPY',
                       'BABA', 'JPM', 'WMT', 'V', 'T', 'UNH', 'PFE', 'INTC', 'VZ', 'ORCL']

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    # await send_stock_details()


@bot.command(name="get_list", help="Gets list of companies for which stock details can be fetched.")
async def get_list(ctx):
    await ctx.send(top_stock_companies)


@bot.command(name="get_stock_data", help="Gets stock data of a specific company for the previous day.")
async def stock_data(ctx, stock_company):

    if stock_company in top_stock_companies:
        stock_company_df = yf.download(stock_company, period="2d")

        msg = create_msg(stock_company, stock_company_df)

        await ctx.send(msg)
    else:
        await ctx.send("Stock data for {stockCompany} doesn't exist!".format(stockCompany=stock_company))


@bot.command(name="create-channel", help="An admin creates a new channel.")
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)

    if not existing_channel:
        print(f'Creating a new channel- {channel_name}...')
        await guild.create_text_channel(channel_name)
        print('Channel created!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Please enter correct usage.')


def create_msg(top_stock_company, top_stock_company_df):
    date = str(top_stock_company_df.head(1).index[0]).split(' ')[0]
    msg = '''\
        {company} EOF Data
        - Date: {Date}
        - Open: {Open}
        - High: {High}
        - Low: {Low}
        - Close: {Close}
        - Adj Close: {Adj_Close}
        - Volume: {Volume}\
     '''.format(company=top_stock_company, Date=date, Open=top_stock_company_df.iat[0, 0], High=top_stock_company_df.iat[0, 1], Low=top_stock_company_df.iat[0, 2], Close=top_stock_company_df.iat[0, 3], Adj_Close=top_stock_company_df.iat[0, 4], Volume=top_stock_company_df.iat[0, 5])

    return msg


@aiocron.crontab('0 18 * * mon-fri')
async def send_stock_details():
    global top_stock_companies

    top_stock_company = random.choice(top_stock_companies)
    top_stock_company_df = yf.download(top_stock_company, period="1d")

    msg = create_msg(top_stock_company, top_stock_company_df)

    existing_channel = discord.utils.get(
        bot.guilds[0].channels, name='stock-details')

    if not existing_channel:
        print(f'Creating a new channel- stock-details...')
        await bot.guilds[0].create_text_channel("stock-details")
        print('Channel created!')
        existing_channel = discord.utils.get(
            bot.guilds[0].channels, name='stock-details')

    await existing_channel.send(msg)


bot.run(TOKEN)
