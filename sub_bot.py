import os
import yfinance as yf
import discord
import plotly.express as px
import matplotlib.pyplot as plt

import datetime

top_stock_companies = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'FB', 'BRK-B', 'SPY',
                       'BABA', 'JPM', 'WMT', 'V', 'T', 'UNH', 'PFE', 'INTC', 'VZ', 'ORCL']


async def send_daily_trade_updates_plot(top_stock_company, existing_channel):
    top_stock_company_df = yf.download(
        top_stock_company, period="1d", interval="1m")

    top_stock_company_df.plot(y='Close', linewidth=0.85)

    plt.xlabel('Datetime')
    plt.ylabel('Close')
    plt.title('Latest stock prices of {company}'.format(
        company=top_stock_company))
    plt.savefig('images/daily_trade_updates_plot_1.png')

    top_stock_company_df.plot(
        y=['Open', 'High', 'Low', 'Close', 'Adj Close'], linewidth=0.85)

    plt.xlabel('Datetime')
    plt.ylabel('Value')
    plt.title('Latest stock prices of {company}'.format(
        company=top_stock_company))
    plt.savefig('images/daily_trade_updates_plot_2.png')

    my_files = [
        discord.File('images/daily_trade_updates_plot_1.png'),
        discord.File('images/daily_trade_updates_plot_2.png')
    ]

    await existing_channel.send('Latest stock prices:', files=my_files)

    os.remove('images/daily_trade_updates_plot_1.png')
    os.remove('images/daily_trade_updates_plot_2.png')


async def send_history_plot(stock_companies, existing_channel):
    df = yf.download(stock_companies[0])
    ax = df.plot(y='Close', label=stock_companies[0], linewidth=0.85)

    for stock_company in stock_companies:
        if stock_company != stock_companies[0]:
            df = yf.download(stock_company)
            df.plot(ax=ax, y='Close', label=stock_company, linewidth=0.85)

    plt.xlabel('Date')
    plt.ylabel('Close')
    plt.title("Historical stock details")

    plt.savefig('images/history.png')

    await existing_channel.send(file=discord.File('images/history.png'))

    os.remove('images/history.png')


async def send_history_plot_in_date_interval(args, existing_channel):
    length = len(args)

    try:
        date_obj1 = datetime.datetime.strptime(args[length-1], '%Y-%m-%d')
        date_obj2 = datetime.datetime.strptime(args[length-2], '%Y-%m-%d')
    except ValueError:
        await existing_channel.send("Incorrect data format, should be YYYY-MM-DD")
        return

    arr = []
    for i in range(length-2):
        arr.append(args[i])
    if set(tuple(arr)).issubset(tuple(top_stock_companies)):
        df = yf.download(arr[0], start=args[length-2], end=args[length-1])
        ax = df.plot(y='Close', label=arr[0], linewidth=0.85)

        for stock_company in arr:
            if stock_company != arr[0]:
                df = yf.download(
                    stock_company, start=args[length-2], end=args[length-1])
                df.plot(ax=ax, y='Close', label=stock_company, linewidth=0.85)

        plt.xlabel('Date')
        plt.ylabel('Close')
        plt.title("Historical stock details for {date1} - {date2}".format(
            date1=args[length-2], date2=args[length-1]))

        plt.savefig('images/history_date_interval.png')

        await existing_channel.send(file=discord.File('images/history_date_interval.png'))

        os.remove('images/history_date_interval.png')
    else:
        await existing_channel.send("Invalid set of companies.")
