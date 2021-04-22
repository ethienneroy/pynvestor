import datetime
import os
import time
from json import JSONEncoder

import numpy
from flask import Flask, render_template
from flask import request
import requests

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import dates
import matplotlib.dates as mdate

from NumpyArrayEncoder import NumpyArrayEncoder
from trade import Trade

plt.style.use('fivethirtyeight')
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def get_history(crypto):
    url = f"https://api-pub.bitfinex.com/v2/candles/trade:5m:t{crypto}USD/hist"
    res = requests.get(url)
    trades = np.array(json.loads(res.text))
    # pd_trades = pd.DataFrame(
    #     {'date': trades[:, 0], 'open': trades[:, 1], 'close': trades[:, 2], 'high': trades[:, 3], 'low': trades[:, 4],
    #      'volume': trades[:, 5]})
    pd_trades = pd.DataFrame(
        {'date': mdate.epoch2num(trades[:, 0]/1000), 'open': trades[:, 1], 'close': trades[:, 2], 'high': trades[:, 3], 'low': trades[:, 4],
         'volume': trades[:, 5]})
    return pd_trades

@app.route('/mfi', methods=["POST"])
def mfi_route():
    cryptocurrency = request.form['crypto']
    trades = get_history(cryptocurrency)

    return calculate_mfi(get_history(cryptocurrency))


@app.route('/chart', methods=["GET"])
def display_chart():
    cryptocurrency = request.args.get('crypto')
    chart = create_chart(get_history(cryptocurrency))
    return render_template("views/chart.html", image='static/my_plot.png')

def calculate_mfi(df):
    typical_price = (df['close'] + df['high'] + df['low']) / 3
    period = 14  # The typical period used for MFI is 14 days
    money_flow = typical_price * df['volume']
    # Get all of the positive and negative money flows
    # where the current typical price is higher than the previous day's typical price, we will append that days money flow to a positive list
    # and where the current typical price is lower than the previous day's typical price, we will append that days money flow to a negative list
    # and set any other value to 0 to be used when summing
    positive_flow = []  # Create a empty list called positive flow
    negative_flow = []  # Create a empty list called negative flow
    # Loop through the typical price
    for i in range(1, len(typical_price)):
        if typical_price[i] > typical_price[
            i - 1]:  # if the present typical price is greater than yesterdays typical price
            positive_flow.append(money_flow[i - 1])  # Then append money flow at position i-1 to the positive flow list
            negative_flow.append(0)  # Append 0 to the negative flow list
        elif typical_price[i] < typical_price[
            i - 1]:  # if the present typical price is less than yesterdays typical price
            negative_flow.append(money_flow[i - 1])  # Then append money flow at position i-1 to negative flow list
            positive_flow.append(0)  # Append 0 to the positive flow list
        else:  # Append 0 if the present typical price is equal to yesterdays typical price
            positive_flow.append(0)
            negative_flow.append(0)

    # Get all of the positive and negative money flows within the time period
    positive_mf = []
    negative_mf = []
    # Get all of the positive money flows within the time period
    for i in range(period - 1, len(positive_flow)):
        positive_mf.append(sum(positive_flow[i + 1 - period: i + 1]))
    # Get all of the negative money flows within the time period
    for i in range(period - 1, len(negative_flow)):
        negative_mf.append(sum(negative_flow[i + 1 - period: i + 1]))

    mfi = 100 * (np.array(positive_mf) / (np.array(positive_mf) + np.array(negative_mf)))
    return json.dumps(mfi, cls=NumpyArrayEncoder)


def convert_trades(data):
    trades = []
    for x in data:
        trades.append(Trade(x))
    return trades


def create_chart(pd_trades):
    plt.figure(figsize=(22.2, 14.5))  # width = 12.2in, height = 4.5
    plt.plot(pd_trades['date'], pd_trades['close'],
             label='Close Price')  # plt.plot( X-Axis , Y-Axis, line_width, alpha_for_blending,  label)
    plt.title('Close Price History')
    plt.xlabel('Date', fontsize=18)
    formatter = dates.DateFormatter('%H:%M:%S')
    ax = plt.gcf().axes[0]
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_minor_locator(dates.MinuteLocator(interval=1))
    ax.xaxis.set_major_locator(dates.MinuteLocator(interval=30))  # every day
    plt.gcf().autofmt_xdate(rotation=25)
    plt.ylabel('Close Price USD ($)', fontsize=18)
    plt.legend(pd_trades.columns.values, loc='upper left')
    filePath = os.path.join('static/my_plot.png')
    if os.path.isfile(filePath):
        os.remove(filePath)
    plt.savefig('static/my_plot.png')
    plt.close()
    plt.show()
    return plt

if __name__ == '__main__':
    app.run()

