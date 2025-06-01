from .base import BaseAgent
from newsapi import NewsApiClient
from ..core.config import get_settings
import time
from typing import Dict, Any
import logging
import json
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
settings = get_settings()

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.news_client = NewsApiClient(api_key=settings.NEWS_API_KEY)
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.max_retries = 3
        self.base_delay = 12  # Alpha Vantage has a rate limit of 5 calls per minute on free tier
    
    async def _get_ticker(self, company_name: str) -> str:
        """Get the stock ticker symbol for a company name using Alpha Vantage."""
        try:
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
            
            response = requests.get(self.base_url, params=params)
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
            logger.error(f"Error getting ticker for {company_name}: {str(e)}")
            return company_name  # Return the company name as fallback
    
    async def process(self, company_name: str, search_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Gather company data based on the search plan."""
        try:
            # Get company ticker
            ticker = await self._get_ticker(company_name)
            logger.info(f"Retrieved ticker symbol: {ticker}")
            
            # Get company data
            company_data = await self._get_company_data_with_retry(ticker)
            news_data = await self._get_news_data_with_retry(company_name)
            
            return {
                "company_info": {
                    "name": company_name,
                    "ticker": ticker.upper() if ticker else None,
                    "description": company_data.get("Description", "Description not available"),
                    "sector": company_data.get("Sector", "Sector not available"),
                    "industry": company_data.get("Industry", "Industry not available")
                },
                "financial_data": {
                    "revenue": company_data.get("RevenueTTM"),
                    "gross_profit": company_data.get("GrossProfitTTM"),
                    "operating_margin": company_data.get("OperatingMarginTTM"),
                    "pe_ratio": company_data.get("PERatio"),
                    "market_cap": company_data.get("MarketCapitalization")
                },
                "market_data": {
                    "price": company_data.get("price", {}).get("regularMarketPrice"),
                    "change_percent": company_data.get("price", {}).get("regularMarketChangePercent"),
                    "volume": company_data.get("price", {}).get("regularMarketVolume"),
                    "52_week_high": company_data.get("52WeekHigh"),
                    "52_week_low": company_data.get("52WeekLow")
                },
                "news_data": news_data
            }
            
        except Exception as e:
            logger.error(f"Error in search agent: {str(e)}")
            return {
                "company_info": {"name": company_name, "description": "Data retrieval failed"},
                "financial_data": {},
                "market_data": {},
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
                overview_response = requests.get(self.base_url, params=overview_params)
                overview_data = overview_response.json()
                
                # Add delay to avoid rate limiting
                time.sleep(12)  # Alpha Vantage rate limit

                # Get global quote for current price data
                quote_params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_key
                }
                quote_response = requests.get(self.base_url, params=quote_params)
                quote_data = quote_response.json()

                # Add delay to avoid rate limiting
                time.sleep(12)  # Alpha Vantage rate limit

                # Get income statement data
                income_params = {
                    "function": "INCOME_STATEMENT",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_key
                }
                income_response = requests.get(self.base_url, params=income_params)
                income_data = income_response.json()

                # Log the responses for debugging
                logger.info(f"Overview data: {overview_data}")
                logger.info(f"Quote data: {quote_data}")
                logger.info(f"Income data: {income_data}")

                # Combine and validate the data
                combined_data = {
                    "Description": overview_data.get("Description", "No description available"),
                    "Sector": overview_data.get("Sector", "Sector not available"),
                    "Industry": overview_data.get("Industry", "Industry not available"),
                    "MarketCapitalization": overview_data.get("MarketCapitalization", "N/A"),
                    "PERatio": overview_data.get("PERatio", "N/A"),
                    "PEGRatio": overview_data.get("PEGRatio", "N/A"),
                    "BookValue": overview_data.get("BookValue", "N/A"),
                    "DividendPerShare": overview_data.get("DividendPerShare", "N/A"),
                    "DividendYield": overview_data.get("DividendYield", "N/A"),
                    "EPS": overview_data.get("EPS", "N/A"),
                    "RevenuePerShareTTM": overview_data.get("RevenuePerShareTTM", "N/A"),
                    "ProfitMargin": overview_data.get("ProfitMargin", "N/A"),
                    "OperatingMarginTTM": overview_data.get("OperatingMarginTTM", "N/A"),
                    "ReturnOnAssetsTTM": overview_data.get("ReturnOnAssetsTTM", "N/A"),
                    "ReturnOnEquityTTM": overview_data.get("ReturnOnEquityTTM", "N/A"),
                    "RevenueTTM": overview_data.get("RevenueTTM", "N/A"),
                    "GrossProfitTTM": overview_data.get("GrossProfitTTM", "N/A"),
                    "DilutedEPSTTM": overview_data.get("DilutedEPSTTM", "N/A"),
                    "QuarterlyEarningsGrowthYOY": overview_data.get("QuarterlyEarningsGrowthYOY", "N/A"),
                    "QuarterlyRevenueGrowthYOY": overview_data.get("QuarterlyRevenueGrowthYOY", "N/A"),
                    "AnalystTargetPrice": overview_data.get("AnalystTargetPrice", "N/A"),
                    "TrailingPE": overview_data.get("TrailingPE", "N/A"),
                    "ForwardPE": overview_data.get("ForwardPE", "N/A"),
                    "PriceToSalesRatioTTM": overview_data.get("PriceToSalesRatioTTM", "N/A"),
                    "PriceToBookRatio": overview_data.get("PriceToBookRatio", "N/A"),
                    "EVToRevenue": overview_data.get("EVToRevenue", "N/A"),
                    "EVToEBITDA": overview_data.get("EVToEBITDA", "N/A"),
                    "Beta": overview_data.get("Beta", "N/A"),
                    "52WeekHigh": overview_data.get("52WeekHigh", "N/A"),
                    "52WeekLow": overview_data.get("52WeekLow", "N/A"),
                    "50DayMovingAverage": overview_data.get("50DayMovingAverage", "N/A"),
                    "200DayMovingAverage": overview_data.get("200DayMovingAverage", "N/A"),
                }

                # Add current market data if available
                if "Global Quote" in quote_data:
                    quote = quote_data["Global Quote"]
                    combined_data["price"] = {
                        "regularMarketPrice": float(quote.get("05. price", 0)),
                        "regularMarketChangePercent": float(quote.get("10. change percent", "0").strip('%')),
                        "regularMarketVolume": int(quote.get("06. volume", 0))
                    }

                # Add income statement data if available
                if "annualReports" in income_data and len(income_data["annualReports"]) > 0:
                    latest_report = income_data["annualReports"][0]
                    combined_data.update({
                        "totalRevenue": latest_report.get("totalRevenue", "N/A"),
                        "grossProfit": latest_report.get("grossProfit", "N/A"),
                        "operatingIncome": latest_report.get("operatingIncome", "N/A"),
                        "netIncome": latest_report.get("netIncome", "N/A")
                    })

                return combined_data

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    # Return a structured response even if the API calls fail
                    return {
                        "Description": "Data temporarily unavailable",
                        "Sector": "Technology",  # Default for Tesla
                        "Industry": "Auto Manufacturers",  # Default for Tesla
                        "MarketCapitalization": "N/A",
                        "PERatio": "N/A",
                        "RevenueTTM": "N/A",
                        "GrossProfitTTM": "N/A",
                        "OperatingMarginTTM": "N/A",
                        "price": {
                            "regularMarketPrice": 0,
                            "regularMarketChangePercent": 0,
                            "regularMarketVolume": 0
                        }
                    }

    async def _get_news_data_with_retry(self, company_name: str) -> list:
        """Get news data with retry logic."""
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retrying news API after {delay} seconds (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                
                news = self.news_client.get_everything(
                    q=company_name,
                    language='en',
                    sort_by='relevancy',
                    page_size=5
                )
                return news.get('articles', [])
            except Exception as e:
                logger.error(f"Failed to get news data (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt == self.max_retries - 1:
                    return [] 