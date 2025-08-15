# scripts/fetch_and_store.py
# This script fetches stock market data from Alpha Vantage and stores it in a PostgreSQL database.

import os
import requests
import psycopg2
from datetime import datetime

# Load environment variables
# Ensure these are set in your environment or in a .env file
API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
DB_HOST = os.environ.get('STOCK_DB_HOST')
DB_PORT = os.environ.get('STOCK_DB_PORT')
DB_NAME = os.environ.get('STOCK_DB_NAME')
DB_USER = os.environ.get('STOCK_DB_USER')
DB_PASSWORD = os.environ.get('STOCK_DB_PASSWORD')
API_URL = 'https://www.alphavantage.co/query'

def get_stock_data(symbol):
    """Fetches daily stock data for a given symbol from Alpha Vantage."""
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY,
        'outputsize': 'compact'
    }
    print(f"Fetching data for symbol: {symbol}")
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status() # Good for catching network-level errors (4xx, 5xx)
        data = response.json()

        print(f"Raw API Response: {data}")

        # Check for specific error messages in the API response.
        # If the API returns an error message, raise an exception.
        # This is useful for catching issues like invalid API keys or exceeded request limits.
        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        
        # Then, check if the expected data key is missing.
        if "Time Series (Daily)" not in data:
            raise ValueError(f"API Error: Unexpected data format. {data.get('Note', '')}")
            
        return data['Time Series (Daily)']
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        raise
    except ValueError as e:
        # This will catch errors related to the API response format or content.
        print(f"Error processing API response: {e}")
        raise

def store_data_in_db(symbol, stock_data):
    """Stores stock data in the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        print("Database connection successful.")

        for date_str, daily_data in stock_data.items():
            trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            open_price = float(daily_data['1. open'])
            high_price = float(daily_data['2. high'])
            low_price = float(daily_data['3. low'])
            close_price = float(daily_data['4. close'])
            volume = int(daily_data['5. volume'])

            insert_query = """
                INSERT INTO stock_data (symbol, trade_date, open_price, high_price, low_price, close_price, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, trade_date) DO UPDATE SET
                    open_price = EXCLUDED.open_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    close_price = EXCLUDED.close_price,
                    volume = EXCLUDED.volume;
            """
            cur.execute(insert_query, (symbol, trade_date, open_price, high_price, low_price, close_price, volume))
        
        conn.commit()
        print(f"Successfully stored/updated {len(stock_data)} records for symbol {symbol}.")
        cur.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()

def run_stock_pipeline(symbol: str):
    """
    Main function to run the stock data pipeline.
    Fetches stock data for the given symbol and stores it in the database.
    """
    print(f"--- Starting stock pipeline for {symbol} ---")
    if not API_KEY or API_KEY == 'YOUR_DEFAULT_API_KEY':
        raise ValueError("Error: ALPHA_VANTAGE_API_KEY environment variable not set.")

    daily_data = get_stock_data(symbol)
    if daily_data:
        store_data_in_db(symbol, daily_data)
    print(f"--- Finished stock pipeline for {symbol} ---")
