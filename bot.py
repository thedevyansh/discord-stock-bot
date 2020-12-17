import os
import datetime
import random
import yfinance as yf
import plotly.express as px
from dotenv import load_dotenv
import discord

import aiocron

# 1
from discord.ext import commands

top_stock_companies = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'FB', 'BRK-B', 'SPY',
                       'BABA', 'JPM', 'WMT', 'V', 'T', 'UNH', 'PFE', 'INTC', 'VZ', 'ORCL']

df_not_none = False
count = 0

if not os.path.exists("images"):
    os.mkdir("images")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name="get_list", help="Gets list of companies for which stock details can be fetched.")
async def get_list(ctx):
    await ctx.send(top_stock_companies)


@bot.command(name="get_stock_data", help="Gets stock data of a specific company for the previous day.")
async def stock_data(ctx, stock_company):

    if stock_company in top_stock_companies:
        stock_company_df = yf.download(stock_company, period="2d")
        msg = create_msg(stock_company, stock_company_df)

        stock_company_df = yf.download(
            stock_company, period="2d", interval="1m")
        fig = px.line(stock_company_df[0: 390], y='Close',
                      title='Stock prices of {company} for previous day'.format(company=stock_company))

        fig.write_image('images/stock_previous_day.png')

        await ctx.send(msg)
        await ctx.send(file=discord.File('images/stock_previous_day.png'))
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


@aiocron.crontab('0 7 * * mon-fri')
async def send_stock_details():

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


# *************************************************************


@aiocron.crontab('30 10-16 * * mon-fri')
async def show_hourly_plot():
    global df_not_none, count
    random_company = ''

    now = datetime.datetime.now()
    if now.hour == 10:
        df_not_none = True
        random_company = random.choice(top_stock_companies)
        df = yf.download(random_company,
                         period="1d", interval="1m")

    elif not df_not_none:
        df_not_none = True

        if count == 0:
            if now.hour == 11:
                count = 1
            elif now.hour == 12:
                count = 2
            elif now.hour == 13:
                count = 3
            elif now.hour == 14:
                count = 4
            elif now.hour == 15:
                count = 5
            else:
                count = 6

        random_company = random.choice(top_stock_companies)
        df = yf.download(random_company,
                         period="1d", interval="1m")

    limiter = 6.5 if (count == 6) else (count + 1)

    fig = px.line(df[60*count: 60*limiter], y='Close',
                  title='Stock prices of {company} for {hour1}:30 - {hour2}:30'.format(company=random_company, hour1=now.hour-1, hour2=now.hour))

    fig.write_image('images/stock_{i}.png'.format(i=count))

    existing_channel = discord.utils.get(
        bot.guilds[0].channels, name='stock-details')

    if not existing_channel:
        print(f'Creating a new channel- stock-details...')
        await bot.guilds[0].create_text_channel("stock-details")
        print('Channel created!')
        existing_channel = discord.utils.get(
            bot.guilds[0].channels, name='stock-details')

    await existing_channel.send(file=discord.File('images/stock_{i}.png'.format(i=count)))

    count = count + 1

    if now.hour == 16:
        df_not_none = False
        count = 0


bot.run(TOKEN)
