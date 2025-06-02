from .base import BaseAgent
from .planning import PlanningAgent
from .search import SearchAgent
from .analysis import AnalysisAgent
from .risk import RiskAgent
from .report import ReportAgent
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.planning_agent = PlanningAgent()
        self.search_agent = SearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.risk_agent = RiskAgent()
        self.report_agent = ReportAgent()
    
    async def process(self, company_name: str):
        try:
            logger.info(f"Starting research process for {company_name}")
            
            # Step 1: Planning
            logger.info("Step 1: Creating research plan")
            search_plan = await self.planning_agent.process(company_name)
            logger.info(f"Research plan created: {search_plan}")
            
            # Step 2: Search and gather data
            logger.info("Step 2: Gathering company data")
            company_data = await self.search_agent.process(company_name, search_plan)
            
            # Check if we got rate limited data
            if company_data.get("company_info", {}).get("description") == "Data temporarily unavailable":
                logger.warning("API rate limit reached, using fallback data")
                company_data = {
                    "company_info": {
                        "name": company_name,
                        "description": "Detailed company information temporarily unavailable due to API rate limits. Please try again later.",
                        "sector": "Information not available",
                        "industry": "Information not available"
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
                        "52_week_high": "N/A",
                        "52_week_low": "N/A"
                    },
                    "market_data": {},
                    "news_data": []
                }
            
            logger.info("Company data gathered successfully")
            
            # Step 3: Financial Analysis
            logger.info("Step 3: Performing financial analysis")
            financial_analysis = await self.analysis_agent.process(company_data)
            logger.info("Financial analysis completed")
            
            # Step 4: Risk Assessment
            logger.info("Step 4: Assessing risks")
            risk_assessment = await self.risk_agent.process(company_data, financial_analysis)
            logger.info("Risk assessment completed")
            
            # Format the response according to CompanyResponse model
            response = {
                "company_info": {
                    "name": company_name,
                    "description": company_data.get("Description", "Company overview not available"),
                    "sector": company_data.get("Sector", "Sector not available"),
                    "industry": company_data.get("Industry", "Industry not available")
                },
                "financial_data": {
                    "revenue": company_data.get("RevenueTTM", "N/A"),
                    "gross_profit": company_data.get("GrossProfitTTM", "N/A"),
                    "operating_margin": company_data.get("OperatingMarginTTM", "N/A"),
                    "pe_ratio": company_data.get("PERatio", "N/A"),
                    "market_cap": company_data.get("MarketCapitalization", "N/A"),
                    "price": company_data.get("price", "N/A"),
                    "change_percent": company_data.get("change_percent", "N/A"),
                    "volume": company_data.get("volume", "N/A"),
                    "week_52_high": company_data.get("52WeekHigh", "N/A"),
                    "week_52_low": company_data.get("52WeekLow", "N/A"),
                    "totalRevenue": company_data.get("totalRevenue", "N/A"),
                    "grossProfit": company_data.get("grossProfit", "N/A"),
                    "operatingIncome": company_data.get("operatingIncome", "N/A"),
                    "netIncome": company_data.get("netIncome", "N/A"),
                    "EPS": company_data.get("EPS", "N/A"),
                    "PERatio": company_data.get("PERatio", "N/A"),
                    "OperatingMarginTTM": company_data.get("OperatingMarginTTM", "N/A"),
                    "ReturnOnEquityTTM": company_data.get("ReturnOnEquityTTM", "N/A"),
                    "ReturnOnAssetsTTM": company_data.get("ReturnOnAssetsTTM", "N/A")
                },
                "financial_analysis": {
                    "financial_health": financial_analysis.get("financial_health", "Financial health analysis not available"),
                    "market_position": financial_analysis.get("market_position", "Market position analysis not available"),
                    "growth_potential": financial_analysis.get("growth_potential", "Growth potential analysis not available"),
                    "key_metrics_analysis": financial_analysis.get("key_metrics_analysis", "Key metrics analysis not available")
                },
                "potential_risks": risk_assessment.get("risks", ["Risk assessment not available"]),
                "news_data": [
                    {
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "publishedAt": article.get("publishedAt", "")
                    }
                    for article in company_data.get("news_data", [])
                ],
                "sources": [article.get("url", "") for article in company_data.get("news_data", [])]
            }
            
            logger.info("Research process completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error in manager workflow: {str(e)}", exc_info=True)
            # Return a structured error response
            return {
                "company_info": {
                    "name": company_name,
                    "description": "Report generation failed. Please try again later.",
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
                "financial_analysis": {
                    "financial_health": "Analysis failed",
                    "market_position": "Analysis failed",
                    "growth_potential": "Analysis failed",
                    "key_metrics_analysis": "Analysis failed"
                },
                "potential_risks": [
                    f"Error during analysis: {str(e)}",
                    "Financial data analysis incomplete",
                    "Market position analysis unavailable",
                    "Regulatory compliance status unknown"
                ],
                "news_data": [],
                "sources": []
            } 