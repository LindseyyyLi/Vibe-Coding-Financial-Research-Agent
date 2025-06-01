from .base import BaseAgent
from typing import Dict, Any
import json

class AnalysisAgent(BaseAgent):
    async def process(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company financial and market data."""
        system_message = """You are a financial analyst. Analyze the company data and provide insights.
        Return a JSON object with these exact keys: financial_health, market_position, growth_potential, and key_metrics_analysis.
        Each key should contain a detailed analysis string."""
        
        # Prepare data for analysis
        analysis_input = {
            "company_info": company_data["company_info"],
            "financial_metrics": {
                **company_data["financial_data"],
                **company_data["market_data"]
            },
            "recent_news": [article["title"] for article in company_data["news_data"]]
        }
        
        prompt = f"""Analyze this company data and provide insights:
        
        Company Information:
        {json.dumps(analysis_input['company_info'], indent=2)}
        
        Financial and Market Metrics:
        {json.dumps(analysis_input['financial_metrics'], indent=2)}
        
        Recent News Headlines:
        {json.dumps(analysis_input['recent_news'], indent=2)}
        
        Return a JSON object with these exact keys and detailed analysis for each:
        {{
            "financial_health": "Analysis of financial stability and performance",
            "market_position": "Analysis of competitive position and market share",
            "growth_potential": "Analysis of future growth opportunities",
            "key_metrics_analysis": "Analysis of important financial ratios and metrics"
        }}
        
        Return ONLY the JSON object, no other text."""
        
        try:
            analysis_text = await self._get_completion(prompt, system_message)
            analysis = json.loads(analysis_text)
            
            # Validate required keys
            required_keys = ["financial_health", "market_position", "growth_potential", "key_metrics_analysis"]
            for key in required_keys:
                if key not in analysis:
                    raise ValueError(f"Missing required key: {key}")
                if not isinstance(analysis[key], str):
                    raise ValueError(f"Value for {key} must be a string")
            
            return analysis
            
        except Exception as e:
            print(f"Error in analysis agent: {str(e)}")
            print(f"Falling back to default analysis")
            
            # Default analysis if AI response fails
            return {
                "financial_health": "Financial health analysis unavailable due to data processing error",
                "market_position": "Market position analysis unavailable due to data processing error",
                "growth_potential": "Growth potential analysis unavailable due to data processing error",
                "key_metrics_analysis": "Key metrics analysis unavailable due to data processing error"
            } 