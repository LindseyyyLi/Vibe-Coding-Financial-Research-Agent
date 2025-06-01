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
                "company_name": company_name,
                "overview": company_data.get("company_info", {}).get("description", "Company overview not available"),
                "financial_metrics": {
                    **(company_data.get("financial_data", {})),
                    **(company_data.get("market_data", {})),
                    "analysis": financial_analysis
                },
                "potential_risks": risk_assessment.get("risks", ["Risk assessment not available"]),
                "sources": [article.get("url", "") for article in company_data.get("news_data", [])]
            }
            
            logger.info("Research process completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error in manager workflow: {str(e)}", exc_info=True)
            # Return a structured error response
            return {
                "company_name": company_name,
                "overview": "Report generation failed. Please try again later.",
                "financial_metrics": {},
                "potential_risks": [
                    f"Error during analysis: {str(e)}",
                    "Financial data analysis incomplete",
                    "Market position analysis unavailable",
                    "Regulatory compliance status unknown"
                ],
                "sources": []
            } 