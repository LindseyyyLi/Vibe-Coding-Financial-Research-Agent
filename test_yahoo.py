import yfinance as yf
import time
import requests

def test_yahoo_finance():
    # List of well-known tickers to test
    tickers = ['AAPL']  # Reduced to just one ticker for testing
    
    print("Testing Yahoo Finance API...")
    
    # Set a custom user agent
    yf.pdr_override()
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'
    
    for ticker in tickers:
        try:
            print(f"\nTrying to get data for {ticker}...")
            
            # Create a Ticker object with the session
            stock = yf.Ticker(ticker, session=session)
            
            # Get historical data first (this often works better than info)
            print("Getting historical data...")
            hist = stock.history(period="1d")
            print(f"Latest closing price: {hist['Close'].iloc[-1] if not hist.empty else 'N/A'}")
            
            # Wait before trying to get more detailed info
            print("Waiting 10 seconds before getting detailed info...")
            time.sleep(10)
            
            # Try to get basic info
            print("Getting company info...")
            info = stock.info
            
            # Print some basic information
            print(f"Company Name: {info.get('longName', 'N/A')}")
            print(f"Current Price: {info.get('currentPrice', 'N/A')}")
            print(f"Market Cap: {info.get('marketCap', 'N/A')}")
            print(f"Industry: {info.get('industry', 'N/A')}")
                
        except Exception as e:
            print(f"Error getting data for {ticker}: {str(e)}")

if __name__ == "__main__":
    test_yahoo_finance() 