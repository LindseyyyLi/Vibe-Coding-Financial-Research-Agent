from .base import BaseAgent
import json
from typing import Dict, Any

class PlanningAgent(BaseAgent):
    async def process(self, company_name: str) -> dict:
        """Plan the research strategy for a given company."""
        system_message = """You are a financial research planning agent. Create a structured research plan for analyzing a company.
        Return a JSON object with exactly these keys: financial_metrics, news_categories, risk_factors, and market_position.
        Each key should contain an array of relevant items to analyze."""
        
        prompt = f"""Create a research plan for {company_name}. The response must be a JSON object with these exact keys and array values:
        {{
            "financial_metrics": ["list of specific financial metrics to analyze"],
            "news_categories": ["list of news categories to monitor"],
            "risk_factors": ["list of risk factors to assess"],
            "market_position": ["list of market position indicators"]
        }}"""
        
        try:
            plan_text = await self._get_completion(prompt, system_message)
            plan = json.loads(plan_text)
            
            # Validate required keys and types
            required_keys = ["financial_metrics", "news_categories", "risk_factors", "market_position"]
            for key in required_keys:
                if key not in plan:
                    raise ValueError(f"Missing required key: {key}")
                if not isinstance(plan[key], list):
                    raise ValueError(f"Value for {key} must be an array")
            
            return plan
            
        except Exception as e:
            print(f"Error in planning agent: {str(e)}")
            print(f"Falling back to default plan")
            
            # Default plan structure if AI response fails
            return {
                "financial_metrics": [
                    "revenue",
                    "net_income",
                    "operating_margin",
                    "cash_flow",
                    "debt_to_equity",
                    "market_cap"
                ],
                "news_categories": [
                    "earnings",
                    "management",
                    "products",
                    "competition",
                    "regulatory"
                ],
                "risk_factors": [
                    "financial_stability",
                    "market_competition",
                    "regulatory_compliance",
                    "operational_efficiency"
                ],
                "market_position": [
                    "market_share",
                    "brand_strength",
                    "competitive_advantage",
                    "growth_potential"
                ]
            } 