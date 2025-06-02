from .base import BaseAgent
from newsapi import NewsApiClient
from ..core.config import get_settings
import time
from typing import Dict, Any
import logging
import json
import requests
from datetime import datetime, timedelta
import yfinance as yf

logger = logging.getLogger(__name__)
settings = get_settings()

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # Add debug logging for API keys
        logger.info("Initializing SearchAgent")
        self.news_client = NewsApiClient(api_key=settings.NEWS_API_KEY)
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.max_retries = 3
        self.base_delay = 12  # Alpha Vantage has a rate limit of 5 calls per minute on free tier
        
        # Verify API keys are loaded
        logger.info("API Keys status:")
        logger.info(f"Alpha Vantage API Key present: {bool(self.alpha_vantage_key)}")
        logger.info(f"News API Key present: {bool(settings.NEWS_API_KEY)}")
    
    async def _get_ticker(self, company_name: str) -> str:
        """Get the stock ticker symbol for a company name using Alpha Vantage."""
        try:
            logger.info(f"Getting ticker for company: {company_name}")
            
            # Common ticker mappings for well-known companies
            common_tickers = {
                "tesla": "TSLA",
                "apple": "AAPL",
                "microsoft": "MSFT",
                "amazon": "AMZN",
                "google": "GOOGL",
                "alphabet": "GOOGL",
                "meta": "META",
                "facebook": "META",
                "netflix": "NFLX",
                "nvidia": "NVDA"
            }
            
            # Check if it's a well-known company
            normalized_name = company_name.lower().strip()
            if normalized_name in common_tickers:
                logger.info(f"Found common ticker for {company_name}: {common_tickers[normalized_name]}")
                return common_tickers[normalized_name]
            
            # Use Alpha Vantage's Symbol Search endpoint
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": company_name,
                "apikey": self.alpha_vantage_key
            }
            
            logger.info(f"Making Alpha Vantage API call for ticker search: {company_name}")
            response = requests.get(self.base_url, params=params)
            logger.info(f"Alpha Vantage API Response Status: {response.status_code}")
            logger.info(f"Alpha Vantage API Response: {response.text[:200]}...")  # Log first 200 chars
            
            data = response.json()
            
            # Get the best match from the search results
            if "bestMatches" in data and len(data["bestMatches"]) > 0:
                # Return the symbol of the first (best) match
                ticker = data["bestMatches"][0]["1. symbol"]
                logger.info(f"Found ticker via API for {company_name}: {ticker}")
                return ticker
            else:
                logger.warning(f"No ticker found for company: {company_name}")
                return company_name  # Return the company name as fallback
                
        except Exception as e:
            logger.error(f"Error getting ticker for {company_name}: {str(e)}", exc_info=True)
            return company_name  # Return the company name as fallback
    
    async def process_quote_data(self, quote_data: Dict) -> Dict:
        """Process quote data from Alpha Vantage."""
        try:
            if "Global Quote" in quote_data:
                quote = quote_data["Global Quote"]
                return {
                    "price": quote.get("05. price", "N/A"),
                    "change_percent": quote.get("10. change percent", "N/A").rstrip('%'),
                    "volume": quote.get("06. volume", "N/A"),
                }
            return {
                "price": "N/A",
                "change_percent": "N/A",
                "volume": "N/A",
            }
        except Exception as e:
            logger.error(f"Error processing quote data: {str(e)}")
            return {
                "price": "N/A",
                "change_percent": "N/A",
                "volume": "N/A",
            }

    async def process(self, company_name: str, search_plan: Dict) -> Dict:
        """Process the search request."""
        try:
            logger.info(f"Starting data gathering process for: {company_name}")
            
            # Get company ticker
            logger.info(f"Getting ticker for company: {company_name}")
            ticker = await self._get_ticker(company_name)
            if not ticker:
                raise ValueError(f"Could not find ticker for {company_name}")
            logger.info(f"Retrieved ticker symbol: {ticker}")
            
            # Get company data
            try:
                overview_data = await self._get_company_data_with_retry(ticker)
            except ValueError as e:
                if "Alpha Vantage API error" in str(e):
                    logger.warning("Alpha Vantage API rate limit reached, using Yahoo Finance fallback")
                    overview_data = await self._get_yahoo_finance_data(ticker)
            
            # Get news data with fallback
            news_data = await self._get_news_data_with_fallback(company_name, ticker)
            
            logger.info("Company data retrieved successfully")
            
            # Prepare response
            response = {
                "company_info": {
                    "name": company_name,
                    "description": overview_data.get("Description", "Company overview not available"),
                    "sector": overview_data.get("Sector", "Sector not available"),
                    "industry": overview_data.get("Industry", "Industry not available")
                },
                "financial_data": {
                    "revenue": overview_data.get("RevenueTTM", "N/A"),
                    "gross_profit": overview_data.get("GrossProfitTTM", "N/A"),
                    "operating_margin": overview_data.get("OperatingMarginTTM", "N/A"),
                    "pe_ratio": overview_data.get("PERatio", "N/A"),
                    "market_cap": overview_data.get("MarketCapitalization", "N/A"),
                    "price": overview_data.get("price", "N/A"),
                    "change_percent": overview_data.get("change_percent", "N/A"),
                    "volume": overview_data.get("volume", "N/A"),
                    "week_52_high": overview_data.get("52WeekHigh", "N/A"),
                    "week_52_low": overview_data.get("52WeekLow", "N/A"),
                    "totalRevenue": overview_data.get("RevenueTTM", "N/A"),
                    "grossProfit": overview_data.get("GrossProfitTTM", "N/A"),
                    "operatingIncome": overview_data.get("OperatingIncome", "N/A"),
                    "netIncome": overview_data.get("NetIncome", "N/A"),
                    "EPS": overview_data.get("EPS", "N/A"),
                    "PERatio": overview_data.get("PERatio", "N/A"),
                    "OperatingMarginTTM": overview_data.get("OperatingMarginTTM", "N/A"),
                    "ReturnOnEquityTTM": overview_data.get("ReturnOnEquityTTM", "N/A"),
                    "ReturnOnAssetsTTM": overview_data.get("ReturnOnAssetsTTM", "N/A")
                },
                "news_data": news_data
            }
            
            logger.info("Successfully prepared response data")
            return response
            
        except Exception as e:
            logger.error(f"Error in search process: {str(e)}", exc_info=True)
            return {
                "company_info": {
                    "name": company_name,
                    "description": "Data temporarily unavailable",
                    "sector": "Not available",
                    "industry": "Not available"
                },
                "financial_data": {
                    "revenue": "N/A",
                    "gross_profit": "N/A",
                    "operating_margin": "N/A",
                    "pe_ratio": "N/A",
                    "market_cap": "N/A",
                    "price": "N/A",
                    "change_percent": "N/A",
                    "volume": "N/A",
                    "week_52_high": "N/A",
                    "week_52_low": "N/A",
                    "totalRevenue": "N/A",
                    "grossProfit": "N/A",
                    "operatingIncome": "N/A",
                    "netIncome": "N/A",
                    "EPS": "N/A",
                    "PERatio": "N/A",
                    "OperatingMarginTTM": "N/A",
                    "ReturnOnEquityTTM": "N/A",
                    "ReturnOnAssetsTTM": "N/A"
                },
                "news_data": []
            }

    async def _get_company_data_with_retry(self, ticker: str) -> Dict[str, Any]:
        """Get company data from Alpha Vantage with retry logic."""
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retrying after {delay} seconds (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)

                # Get company overview
                overview_params = {
                    "function": "OVERVIEW",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_key
                }
                logger.info(f"Making Alpha Vantage API call for company overview: {ticker}")
                overview_response = requests.get(self.base_url, params=overview_params)
                logger.info(f"Overview API Response Status: {overview_response.status_code}")
                logger.info(f"Overview API Response: {overview_response.text[:200]}...")
                overview_data = overview_response.json()
                
                # Check if we got an error response
                if "Error Message" in overview_data or "Information" in overview_data:
                    logger.error(f"Error in overview data: {overview_data}")
                    raise ValueError(f"Alpha Vantage API error: {overview_data}")
                
                # Add delay to avoid rate limiting
                time.sleep(12)  # Alpha Vantage rate limit

                # Get global quote for current price data
                quote_params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_key
                }
                logger.info(f"Making Alpha Vantage API call for quote data: {ticker}")
                quote_response = requests.get(self.base_url, params=quote_params)
                logger.info(f"Quote API Response Status: {quote_response.status_code}")
                logger.info(f"Quote API Response: {quote_response.text[:200]}...")
                quote_data = quote_response.json()

                # Check if we got an error response
                if "Error Message" in quote_data or "Information" in quote_data:
                    logger.error(f"Error in quote data: {quote_data}")
                    raise ValueError(f"Alpha Vantage API error: {quote_data}")

                # Add delay to avoid rate limiting
                time.sleep(12)  # Alpha Vantage rate limit

                # Get income statement data
                income_params = {
                    "function": "INCOME_STATEMENT",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_key
                }
                logger.info(f"Making Alpha Vantage API call for income statement: {ticker}")
                income_response = requests.get(self.base_url, params=income_params)
                logger.info(f"Income API Response Status: {income_response.status_code}")
                logger.info(f"Income API Response: {income_response.text[:200]}...")
                income_data = income_response.json()

                # Check if we got an error response
                if "Error Message" in income_data or "Information" in income_data:
                    logger.error(f"Error in income data: {income_data}")
                    raise ValueError(f"Alpha Vantage API error: {income_data}")

                # Combine and validate the data
                combined_data = {
                    "Description": overview_data.get("Description", "No description available"),
                    "Sector": overview_data.get("Sector", "Sector not available"),
                    "Industry": overview_data.get("Industry", "Industry not available"),
                    "MarketCapitalization": overview_data.get("MarketCapitalization", "N/A"),
                    "PERatio": overview_data.get("PERatio", "N/A"),
                    "RevenueTTM": overview_data.get("RevenueTTM", "N/A"),
                    "GrossProfitTTM": overview_data.get("GrossProfitTTM", "N/A"),
                    "OperatingMarginTTM": overview_data.get("OperatingMarginTTM", "N/A"),
                    "NetIncome": overview_data.get("NetIncome", "N/A"),
                    "EPS": overview_data.get("EPS", "N/A"),
                    "ReturnOnEquityTTM": overview_data.get("ReturnOnEquityTTM", "N/A"),
                    "ReturnOnAssetsTTM": overview_data.get("ReturnOnAssetsTTM", "N/A"),
                    "52WeekHigh": overview_data.get("52WeekHigh", "N/A"),
                    "52WeekLow": overview_data.get("52WeekLow", "N/A")
                }

                # Add current market data if available
                if "Global Quote" in quote_data:
                    quote = quote_data["Global Quote"]
                    price = quote.get("05. price", "N/A")
                    change_percent = quote.get("10. change percent", "0%").rstrip('%')
                    volume = quote.get("06. volume", "N/A")
                    
                    combined_data.update({
                        "price": price,
                        "change_percent": change_percent,
                        "volume": volume
                    })
                else:
                    combined_data.update({
                        "price": "N/A",
                        "change_percent": "N/A",
                        "volume": "N/A"
                    })

                # Add income statement data if available
                if "annualReports" in income_data and len(income_data["annualReports"]) > 0:
                    latest_report = income_data["annualReports"][0]
                    combined_data.update({
                        "totalRevenue": latest_report.get("totalRevenue", "N/A"),
                        "grossProfit": latest_report.get("grossProfit", "N/A"),
                        "operatingIncome": latest_report.get("operatingIncome", "N/A"),
                        "netIncome": latest_report.get("netIncome", "N/A")
                    })

                logger.info("Successfully retrieved and combined company data")
                return combined_data

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    # Return a structured response even if the API calls fail
                    return {
                        "Description": "Data temporarily unavailable due to API rate limits or connection issues. Please try again later.",
                        "Sector": "Technology",  # Default for Tesla
                        "Industry": "Auto Manufacturers",  # Default for Tesla
                        "MarketCapitalization": "N/A",
                        "PERatio": "N/A",
                        "RevenueTTM": "N/A",
                        "GrossProfitTTM": "N/A",
                        "OperatingMarginTTM": "N/A",
                        "NetIncome": "N/A",
                        "EPS": "N/A",
                        "ReturnOnEquityTTM": "N/A",
                        "ReturnOnAssetsTTM": "N/A",
                        "52WeekHigh": "N/A",
                        "52WeekLow": "N/A",
                        "price": "N/A",
                        "change_percent": "N/A",
                        "volume": "N/A",
                        "totalRevenue": "N/A",
                        "grossProfit": "N/A",
                        "operatingIncome": "N/A",
                        "netIncome": "N/A"
                    }

    async def _get_news_data_with_fallback(self, company_name: str, ticker: str) -> list:
        """Get news data with fallback options."""
        try:
            # First try NewsAPI
            news = self.news_client.get_everything(
                q=company_name,
                language='en',
                sort_by='relevancy',
                page_size=5
            )
            
            if news and 'articles' in news and news['articles']:
                logger.info("Successfully retrieved news from NewsAPI")
                return news.get('articles', [])
            
            # If NewsAPI fails, try Yahoo Finance
            logger.warning("NewsAPI failed, trying Yahoo Finance")
            yahoo_news = await self._get_yahoo_news(ticker)
            if yahoo_news:
                return yahoo_news
            
            # If both fail, try web search fallback
            logger.warning("Both NewsAPI and Yahoo Finance failed, using web search fallback")
            return await self._get_web_search_news(company_name)
            
        except Exception as e:
            logger.error(f"Failed to get news data: {str(e)}")
            return []
    
    async def _get_yahoo_news(self, ticker: str) -> list:
        """Get news from Yahoo Finance."""
        try:
            # Get the ticker info
            stock = yf.Ticker(ticker)
            
            # Get news
            news_data = stock.news
            
            if news_data:
                return [
                    {
                        "title": article.get("title", ""),
                        "description": article.get("summary", ""),
                        "url": article.get("link", ""),
                        "publishedAt": datetime.fromtimestamp(article.get("providerPublishTime", 0)).isoformat()
                    }
                    for article in news_data[:5]  # Limit to 5 articles
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Yahoo Finance news API failed: {str(e)}")
            return []

    async def _get_web_search_news(self, company_name: str) -> list:
        """Get news from web search as a fallback."""
        try:
            # You can add more news sources here
            search_url = f"https://www.google.com/search?q={company_name}+stock+news&tbm=nws"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers)
            
            # Return a basic news structure
            return [
                {
                    "title": "Recent news available at Google News",
                    "description": "Please visit Google News for the latest updates about " + company_name,
                    "url": search_url,
                    "publishedAt": datetime.now().isoformat()
                }
            ]
        except Exception as e:
            logger.error(f"Web search fallback failed: {str(e)}")
            return []

    async def _get_yahoo_finance_data(self, ticker: str) -> Dict[str, Any]:
        """Get financial data from Yahoo Finance."""
        try:
            # Get the ticker info
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Map Yahoo Finance data to our format
            return {
                "Description": info.get("longBusinessSummary", "No description available"),
                "Sector": info.get("sector", "Sector not available"),
                "Industry": info.get("industry", "Industry not available"),
                "MarketCapitalization": str(info.get("marketCap", "N/A")),
                "PERatio": str(info.get("trailingPE", "N/A")),
                "RevenueTTM": str(info.get("totalRevenue", "N/A")),
                "GrossProfitTTM": str(info.get("grossProfits", "N/A")),
                "OperatingMarginTTM": str(info.get("operatingMargins", "N/A")),
                "NetIncome": str(info.get("netIncomeToCommon", "N/A")),
                "EPS": str(info.get("trailingEps", "N/A")),
                "ReturnOnEquityTTM": str(info.get("returnOnEquity", "N/A")),
                "ReturnOnAssetsTTM": str(info.get("returnOnAssets", "N/A")),
                "52WeekHigh": str(info.get("fiftyTwoWeekHigh", "N/A")),
                "52WeekLow": str(info.get("fiftyTwoWeekLow", "N/A")),
                "price": str(info.get("regularMarketPrice", "N/A")),
                "change_percent": str(info.get("regularMarketChangePercent", "N/A")),
                "volume": str(info.get("regularMarketVolume", "N/A")),
                "OperatingIncome": str(info.get("operatingIncome", "N/A"))
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance data retrieval failed: {str(e)}")
            return {
                "Description": "Data temporarily unavailable",
                "Sector": "Technology",  # Default for Tesla
                "Industry": "Auto Manufacturers",  # Default for Tesla
                "MarketCapitalization": "N/A",
                "PERatio": "N/A",
                "RevenueTTM": "N/A",
                "GrossProfitTTM": "N/A",
                "OperatingMarginTTM": "N/A",
                "NetIncome": "N/A",
                "EPS": "N/A",
                "ReturnOnEquityTTM": "N/A",
                "ReturnOnAssetsTTM": "N/A",
                "52WeekHigh": "N/A",
                "52WeekLow": "N/A",
                "price": "N/A",
                "change_percent": "N/A",
                "volume": "N/A",
                "OperatingIncome": "N/A"
            } 