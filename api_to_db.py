#!/anaconda3/envs/dsi/bin/python


#  API restrictions:
#  - 5 requests per minute
#  - 500 requests per day
# 
# This script makes 3 calls per run

from config import API_KEY

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

from sqlalchemy import create_engine
import pandas as pd
import random
import sys
import time


def ticker_to_db(ticker, interval='5min', outputsize='full'):
    # Create API objects
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    ti = TechIndicators(key=API_KEY, output_format='pandas')
    
    # Get stock price data
    df, _ = ts.get_intraday(ticker, interval=interval, outputsize=outputsize)
    
    # Process df
    df.drop(columns='5. volume', inplace=True)
    df.sort_index(ascending=True, inplace=True)

    df.rename(columns={"1. open": "open",
                       "2. high": "high",
                       "3. low": "low",
                       "4. close": "close"}, 
              inplace=True)

    if len(df.iloc[0].name) == 19:
        df.index = df.index.map(lambda x: x[:-3])
        
    # Get sma data
    sma8, _ = ti.get_sma(ticker, interval=interval, time_period=8, series_type='close')
    sma13, _ = ti.get_sma(ticker, interval=interval, time_period=13, series_type='close')
    
    # Rename cols
    sma8.rename(columns={"SMA": "sma8"}, inplace=True)
    sma13.rename(columns={"SMA": "sma13"}, inplace=True)

    df = df.join(sma8, how='inner').join(sma13, how='inner')

    df.reset_index(inplace=True)

    # Create ticker col
    df.insert(0, 'ticker', ticker)

    # Create new columns for 'buy' trigger
    df['sma8<sma13'] = df.sma8<df.sma13

    df['sma_buy'] = 0

    # Starting on index 2, so we can reference the two previous rows
    # If sma8 < sma13 two rows ago, and sma8 > sma13 1 row ago,
    # indicate "buy" on current row

    for i in range(2, len(df)+1):
        if (df.loc[i-2, 'sma8<sma13']) and (df.loc[i-1, 'sma8<sma13'] == False):
            df.loc[i, 'sma_buy'] = 1

    # Create an empty column for wins
    df["sma_win"] = 0

    # Populate 'sma_win' with 0 or 1 based on exit conditions

    # Get indexes where buy is 1 (True)
    buy_idxs = df.index[df['sma_buy']==1].tolist()

    for idx in buy_idxs:
        purch_price = df.loc[idx, 'open']
        upper_lim = purch_price * 1.01
        lower_lim = purch_price * 0.997
        for i in range(idx, len(df)):
            if (df.loc[i, ["high", "low", "close"]]<=lower_lim).any():
                break
            elif (df.loc[i, ["high", "low", "close"]]>=upper_lim).any():
                df.at[idx, "sma_win"] = 1
                break
            elif i == len(df):
                break

    # Populate df with 'random' buys and wins
    df['rnd_buy'] = 0
    df['rnd_win'] = 0

    # Generate a number of random buys +/- 10% of number of sma buys
    rnd_buys = int(df.sma_buy.sum() * random.uniform(0.9, 1.1))

    # List of random indexes to 'buy'
    rnd_idxs = random.sample(range(len(df)), rnd_buys)

    df.loc[rnd_idxs, 'rnd_buy'] = 1

    for idx in rnd_idxs:
        purch_price = df.loc[idx, 'open']
        upper_lim = purch_price * 1.01
        lower_lim = purch_price * 0.997
        for i in range(idx, len(df)):
            if (df.loc[i, ["high", "low", "close"]]<=lower_lim).any():
                break
            elif (df.loc[i, ["high", "low", "close"]]>=upper_lim).any():
                df.at[idx, "rnd_win"] = 1
                break
            elif i == len(df):
                break
    
    # Store in Postgres db

    # Set db variables
    user = 'anthony'
    pw = 'pw'
    host = 'localhost:5432'
    db_name = 'indicator_tests'
    table = 'sma_nasdaq'

    # Create engine for interacting with db
    engine = create_engine(f'postgresql+psycopg2://{user}:{pw}@{host}/{db_name}')

    # Append to db
    df.to_sql(table, engine, if_exists='append')


def main(csv, start, stop):
    rnd_ls = pd.read_csv(csv)['Symbol'].tolist()
    
    if stop == 'end':
        stop = None
        
    for ticker in rnd_ls[start:stop]:
        try:
            ticker_to_db(ticker)
            print(f'Successfully processed {ticker}')
        except:
            print(f'Error when processing: {ticker}')
        time.sleep(60)
    


if __name__ == "__main__":
    _, csv, start, stop = sys.argv
    main(csv, start, stop)


