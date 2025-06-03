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
from fastapi import HTTPException

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
                    "price": float(quote.get("05. price", 0)),
                    "change_percent": float(quote.get("10. change percent", "0").rstrip('%')),
                    "volume": int(quote.get("06. volume", 0)),
                }
            return {
                "price": 0.0,
                "change_percent": 0.0,
                "volume": 0,
            }
        except Exception as e:
            logger.error(f"Error processing quote data: {str(e)}")
            return {
                "price": 0.0,
                "change_percent": 0.0,
                "volume": 0,
            }

    async def process(self, company_name: str, search_plan: Dict) -> Dict:
        """Process the search request."""
        error_details = []
        try:
            logger.info(f"Starting data gathering process for: {company_name}")
            
            # Get company ticker
            logger.info(f"Getting ticker for company: {company_name}")
            ticker = await self._get_ticker(company_name)
            if not ticker:
                raise ValueError(f"Could not find ticker for {company_name}")
            logger.info(f"Retrieved ticker symbol: {ticker}")
            
            # Get company data
            overview_data = None
            
            try:
                logger.info("Attempting to get data from Alpha Vantage")
                overview_data = await self._get_company_data_with_retry(ticker)
                if not overview_data:
                    raise ValueError("Empty response from Alpha Vantage")
                logger.info(f"Successfully retrieved data from Alpha Vantage: {str(overview_data)[:200]}")
            except Exception as e:
                error_msg = f"Alpha Vantage API error: {str(e)}"
                logger.warning(error_msg)
                error_details.append(error_msg)
                
                logger.info("Falling back to Yahoo Finance")
                try:
                    overview_data = await self._get_yahoo_finance_data(ticker)
                    if not overview_data:
                        raise ValueError("Empty response from Yahoo Finance")
                    logger.info(f"Successfully retrieved data from Yahoo Finance: {str(overview_data)[:200]}")
                except Exception as e:
                    error_msg = f"Yahoo Finance API error: {str(e)}"
                    logger.error(error_msg)
                    error_details.append(error_msg)
                    raise ValueError(f"Both data sources failed. Errors: {', '.join(error_details)}")
            
            if not overview_data:
                raise ValueError("No data retrieved from any source")
            
            # Get news data with fallback
            news_data = []
            try:
                news_data = await self._get_news_data_with_fallback(company_name, ticker)
            except Exception as e:
                error_msg = f"Error fetching news data: {str(e)}"
                logger.error(error_msg)
                error_details.append(error_msg)
            
            # Validate required fields
            required_fields = {
                "price": overview_data.get("regularMarketPrice", overview_data.get("price")),
                "change_percent": overview_data.get("regularMarketChangePercent", overview_data.get("change_percent")),
                "volume": overview_data.get("regularMarketVolume", overview_data.get("volume"))
            }
            
            missing_fields = [field for field, value in required_fields.items() if value is None or value == 0]
            if missing_fields:
                error_msg = f"Missing or invalid required fields: {', '.join(missing_fields)}"
                logger.error(error_msg)
                error_details.append(error_msg)
                raise ValueError(error_msg)
            
            # Prepare response with detailed logging
            response = {
                "company_info": {
                    "name": company_name,
                    "description": overview_data.get("Description", overview_data.get("description", "N/A")),
                    "sector": overview_data.get("Sector", overview_data.get("sector", "N/A")),
                    "industry": overview_data.get("Industry", overview_data.get("industry", "N/A"))
                },
                "financial_data": {
                    "revenue": overview_data.get("RevenueTTM", overview_data.get("totalRevenue", "N/A")),
                    "gross_profit": overview_data.get("GrossProfitTTM", overview_data.get("grossProfit", "N/A")),
                    "operating_margin": overview_data.get("OperatingMarginTTM", overview_data.get("operatingMargins", "N/A")),
                    "pe_ratio": overview_data.get("PERatio", overview_data.get("trailingPE", "N/A")),
                    "market_cap": overview_data.get("MarketCapitalization", "N/A"),
                    "price": float(required_fields["price"]),
                    "change_percent": float(required_fields["change_percent"]),
                    "volume": int(required_fields["volume"]),
                    "week_52_high": overview_data.get("52WeekHigh", "N/A"),
                    "week_52_low": overview_data.get("52WeekLow", "N/A"),
                    "totalRevenue": overview_data.get("totalRevenue", overview_data.get("RevenueTTM", "N/A")),
                    "grossProfit": overview_data.get("grossProfit", overview_data.get("GrossProfitTTM", "N/A")),
                    "operatingIncome": overview_data.get("operatingIncome", overview_data.get("OperatingIncome", "N/A")),
                    "netIncome": overview_data.get("netIncome", overview_data.get("NetIncome", "N/A")),
                    "EPS": overview_data.get("EPS", overview_data.get("trailingEps", "N/A")),
                    "PERatio": overview_data.get("PERatio", overview_data.get("trailingPE", "N/A")),
                    "OperatingMarginTTM": overview_data.get("OperatingMarginTTM", overview_data.get("operatingMargins", "N/A")),
                    "ReturnOnEquityTTM": overview_data.get("ReturnOnEquityTTM", overview_data.get("returnOnEquity", "N/A")),
                    "ReturnOnAssetsTTM": overview_data.get("ReturnOnAssetsTTM", overview_data.get("returnOnAssets", "N/A")),
                    "Beta": overview_data.get("Beta", "N/A"),
                    "50DayMovingAverage": overview_data.get("50DayMovingAverage", "N/A"),
                    "200DayMovingAverage": overview_data.get("200DayMovingAverage", "N/A")
                },
                "market_data": {
                    "regularMarketPrice": float(required_fields["price"]),
                    "regularMarketChangePercent": float(required_fields["change_percent"]),
                    "regularMarketVolume": int(required_fields["volume"]),
                    "MarketCapitalization": overview_data.get("MarketCapitalization", "N/A"),
                    "Beta": overview_data.get("Beta", "N/A"),
                    "52WeekHigh": overview_data.get("52WeekHigh", "N/A"),
                    "52WeekLow": overview_data.get("52WeekLow", "N/A"),
                    "50DayMovingAverage": overview_data.get("50DayMovingAverage", "N/A"),
                    "200DayMovingAverage": overview_data.get("200DayMovingAverage", "N/A")
                },
                "news_data": news_data,
                "error_details": error_details if error_details else None
            }
            
            # Log the response data
            logger.info(f"Successfully prepared response data: {str(response)[:200]}")
            return response
            
        except Exception as e:
            error_msg = f"Search process failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            error_details.append(error_msg)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to process company research",
                    "message": str(e),
                    "error_details": error_details
                }
            )

    async def _get_company_data_with_retry(self, ticker: str) -> Dict[str, Any]:
        """Get company data from Alpha Vantage with retry logic."""
        last_error = None
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
                
                if overview_response.status_code != 200:
                    raise ValueError(f"Overview API failed with status code: {overview_response.status_code}")
                
                overview_data = overview_response.json()
                logger.info(f"Overview API Response: {str(overview_data)[:200]}...")
                
                # Check if we got an error response or empty data
                if not overview_data or len(overview_data) <= 1:
                    raise ValueError("Empty response from overview API")
                if "Error Message" in overview_data:
                    raise ValueError(f"Alpha Vantage API error in overview: {overview_data['Error Message']}")
                if "Information" in overview_data:
                    raise ValueError(f"Alpha Vantage API limit: {overview_data['Information']}")
                
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
                
                if quote_response.status_code != 200:
                    raise ValueError(f"Quote API failed with status code: {quote_response.status_code}")
                
                quote_data = quote_response.json()
                logger.info(f"Quote API Response: {str(quote_data)[:200]}...")

                # Check if we got an error response or empty data
                if not quote_data or "Global Quote" not in quote_data or not quote_data["Global Quote"]:
                    raise ValueError("Empty response from quote API")
                if "Error Message" in quote_data:
                    raise ValueError(f"Alpha Vantage API error in quote: {quote_data['Error Message']}")
                if "Information" in quote_data:
                    raise ValueError(f"Alpha Vantage API limit: {quote_data['Information']}")

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
                
                if income_response.status_code != 200:
                    raise ValueError(f"Income API failed with status code: {income_response.status_code}")
                
                income_data = income_response.json()
                logger.info(f"Income API Response: {str(income_data)[:200]}...")

                # Check if we got an error response or empty data
                if not income_data or "annualReports" not in income_data or not income_data["annualReports"]:
                    raise ValueError("Empty response from income API")
                if "Error Message" in income_data:
                    raise ValueError(f"Alpha Vantage API error in income: {income_data['Error Message']}")
                if "Information" in income_data:
                    raise ValueError(f"Alpha Vantage API limit: {income_data['Information']}")

                # Process quote data
                quote_info = {}
                if "Global Quote" in quote_data:
                    quote = quote_data["Global Quote"]
                    try:
                        quote_info = {
                            "regularMarketPrice": float(quote.get("05. price", 0)),
                            "regularMarketChangePercent": float(quote.get("10. change percent", "0").rstrip('%')),
                            "regularMarketVolume": int(quote.get("06. volume", 0)),
                            "price": float(quote.get("05. price", 0)),
                            "change_percent": float(quote.get("10. change percent", "0").rstrip('%')),
                            "volume": int(quote.get("06. volume", 0))
                        }
                    except (ValueError, TypeError) as e:
                        raise ValueError(f"Error processing quote data: {str(e)}")

                # Process income statement data
                income_info = {}
                if "annualReports" in income_data and len(income_data["annualReports"]) > 0:
                    latest_report = income_data["annualReports"][0]
                    try:
                        income_info = {
                            "totalRevenue": latest_report.get("totalRevenue"),
                            "grossProfit": latest_report.get("grossProfit"),
                            "operatingIncome": latest_report.get("operatingIncome"),
                            "netIncome": latest_report.get("netIncome")
                        }
                    except Exception as e:
                        raise ValueError(f"Error processing income data: {str(e)}")

                # Combine all data
                combined_data = {
                    **overview_data,  # Base data from overview
                    **quote_info,     # Add quote data
                    **income_info     # Add income statement data
                }

                # Validate combined data
                if not any(value for value in combined_data.values() if value not in [None, "", "None", "N/A", 0]):
                    raise ValueError("No valid data after combining all sources")

                logger.info(f"Successfully combined all data: {str(combined_data)[:200]}...")
                return combined_data

            except Exception as e:
                last_error = str(e)
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed: {last_error}")
                if attempt == self.max_retries - 1:
                    raise ValueError(f"All Alpha Vantage attempts failed: {last_error}")
                    
    async def _get_yahoo_finance_data(self, ticker: str) -> Dict[str, Any]:
        """Get financial data from Yahoo Finance."""
        try:
            logger.info(f"Fetching Yahoo Finance data for ticker: {ticker}")
            # Get the ticker info
            stock = yf.Ticker(ticker)
            
            # Get both info and financials
            info = stock.info
            if not info:
                raise ValueError("No data received from Yahoo Finance info")
            logger.info(f"Received Yahoo Finance info data: {str(info)[:200]}...")
            
            # Get additional financial data
            try:
                financials = stock.financials.iloc[0] if not stock.financials.empty else {}
                balance_sheet = stock.balance_sheet.iloc[0] if not stock.balance_sheet.empty else {}
                logger.info("Successfully retrieved additional financial data")
            except Exception as e:
                logger.warning(f"Could not get detailed financials: {str(e)}")
                financials = {}
                balance_sheet = {}
            
            # Validate required fields
            required_fields = {
                "regularMarketPrice": info.get("regularMarketPrice", info.get("currentPrice")),
                "regularMarketVolume": info.get("regularMarketVolume", info.get("volume")),
                "sector": info.get("sector"),
                "industry": info.get("industry")
            }
            
            missing_fields = [field for field, value in required_fields.items() if value is None]
            if missing_fields:
                raise ValueError(f"Missing required fields from Yahoo Finance: {', '.join(missing_fields)}")
            
            # Map Yahoo Finance data to our format with detailed logging
            data = {
                "Description": info.get("longBusinessSummary", info.get("description")),
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
                "MarketCapitalization": str(info.get("marketCap")),
                "PERatio": str(info.get("trailingPE", info.get("forwardPE"))),
                "RevenueTTM": str(info.get("totalRevenue", financials.get("Total Revenue"))),
                "GrossProfitTTM": str(info.get("grossProfits", financials.get("Gross Profit"))),
                "OperatingMarginTTM": str(info.get("operatingMargins")),
                "NetIncome": str(info.get("netIncomeToCommon", financials.get("Net Income"))),
                "EPS": str(info.get("trailingEps", info.get("forwardEps"))),
                "ReturnOnEquityTTM": str(info.get("returnOnEquity")),
                "ReturnOnAssetsTTM": str(info.get("returnOnAssets")),
                "52WeekHigh": str(info.get("fiftyTwoWeekHigh")),
                "52WeekLow": str(info.get("fiftyTwoWeekLow")),
                "regularMarketPrice": float(info.get("regularMarketPrice", info.get("currentPrice", 0))),
                "regularMarketChangePercent": float(info.get("regularMarketChangePercent", info.get("priceToSalesTrailing12Months", 0))),
                "regularMarketVolume": int(info.get("regularMarketVolume", info.get("volume", 0))),
                "price": float(info.get("regularMarketPrice", info.get("currentPrice", 0))),
                "change_percent": float(info.get("regularMarketChangePercent", info.get("priceToSalesTrailing12Months", 0))),
                "volume": int(info.get("regularMarketVolume", info.get("volume", 0))),
                "OperatingIncome": str(info.get("operatingIncome", financials.get("Operating Income"))),
                "Beta": str(info.get("beta")),
                "50DayMovingAverage": str(info.get("fiftyDayAverage")),
                "200DayMovingAverage": str(info.get("twoHundredDayAverage"))
            }
            
            # Validate the data
            if not any(value for value in data.values() if value not in [None, "None", "0", 0]):
                raise ValueError("No valid data retrieved from Yahoo Finance")
            
            logger.info(f"Processed Yahoo Finance data: {str(data)[:200]}...")
            return data
            
        except Exception as e:
            logger.error(f"Yahoo Finance data retrieval failed: {str(e)}", exc_info=True)
            raise ValueError(f"Yahoo Finance error: {str(e)}")

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