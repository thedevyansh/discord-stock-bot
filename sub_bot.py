import yfinance as yf
import discord
import plotly.express as px


async def send_daily_trade_updates_plot(top_stock_company, existing_channel):
    top_stock_company_df = yf.download(
        top_stock_company, period="1d", interval="1m")

    fig = px.line(top_stock_company_df, y='Close',
                  title='Latest stock prices of {company}'.format(company=top_stock_company))
    fig.write_image('images/daily_trade_updates_plot_1.png')

    fig = px.line(top_stock_company_df, y=['Open', 'High', 'Low', 'Close', 'Adj Close'],
                  title='Latest stock prices of {company}'.format(company=top_stock_company))
    fig.write_image('images/daily_trade_updates_plot_2.png')

    await existing_channel.send(file=discord.File('images/daily_trade_updates_plot_1.png'))
    await existing_channel.send(file=discord.File('images/daily_trade_updates_plot_2.png'))
