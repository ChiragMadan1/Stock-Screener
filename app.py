import yfinance as yf
import os, csv
import pandas as pd
import talib
from flask import Flask, render_template, request
from patterns import patterns

app = Flask(__name__)

@app.route('/')
def home_page():
    current_pattern = request.args.get('pattern', None)
    stocks = {}

    with open('datasets/companies.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}
    
    print(stocks)

    if current_pattern:
        datafiles = os.listdir('datasets/daily')
        for filename in datafiles:
            df = pd.read_csv('datasets/daily/{}'.format(filename))
            pattern_func = getattr(talib, current_pattern)
            symbol = filename.split('.')[0]

            try:
                result = pattern_func(df['Open'], df['High'], df['Low'], df['Close'])
                last = result.tail(1).values[0]

                if last > 0:
                    stocks[symbol][current_pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][current_pattern] = 'bearish'
                else:
                    stocks[symbol][current_pattern] = None

            except:
                pass

    return render_template('index.html', patterns=patterns, stocks=stocks ,current_pattern=current_pattern)

@app.route('/snapshot')
def snapshot():
    with open('datasets/companies.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            df = yf.download(symbol, start="2021-01-02")
            df.to_csv('datasets/daily/{}.csv'.format(symbol))

    return('Code Executed')
    