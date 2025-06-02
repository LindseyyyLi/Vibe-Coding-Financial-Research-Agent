from .base import BaseAgent
from typing import Dict, Any, List
import json

class RiskAgent(BaseAgent):
    async def process(self, company_data: Dict[str, Any], financial_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify potential risks and red flags."""
        system_message = """You are a risk assessment specialist. Analyze the company data and financial analysis to 
        identify potential risks and red flags. Focus on financial, operational, market, and regulatory risks.
        IMPORTANT: Return ONLY a JSON object with a 'risks' array containing risk statements."""
        
        # Prepare data for risk assessment
        risk_input = {
            "company_info": company_data["company_info"],
            "financial_data": company_data["financial_data"],
            "market_data": company_data["market_data"],
            "news_data": company_data["news_data"],
            "financial_analysis": financial_analysis
        }
        
        prompt = f"""Analyze the following company data for potential risks:
        
        Company Information:
        {json.dumps(risk_input['company_info'], indent=2)}
        
        Financial Data:
        {json.dumps(risk_input['financial_data'], indent=2)}
        
        Market Data:
        {json.dumps(risk_input['market_data'], indent=2)}
        
        Recent News:
        {json.dumps([article["title"] for article in risk_input['news_data']], indent=2)}
        
        Financial Analysis:
        {json.dumps(risk_input['financial_analysis'], indent=2)}
        
        Return a JSON object with a 'risks' array containing risk statements in these categories:
        1. Financial Risks
        2. Operational Risks
        3. Market Risks
        4. Regulatory Risks
        
        Example format:
        {{"risks": [
                "High debt-to-equity ratio indicates financial risk",
                "Supply chain concentration in single region",
                "Increasing market competition from new entrants",
                "Pending regulatory changes may impact operations"
        ]}}
        
        Return ONLY the JSON object, no other text or formatting."""
        
        risk_text = await self._get_completion(prompt, system_message)
        
        try:
            # Clean the response of any markdown or extra text
            risk_text = risk_text.strip()
            if risk_text.startswith('```'):
                risk_text = risk_text.split('```')[1]
                if risk_text.startswith('json'):
                    risk_text = risk_text[4:]
            risk_text = risk_text.strip()
            
            risks = json.loads(risk_text)
            
            # Validate the structure
            if not isinstance(risks, dict) or 'risks' not in risks or not isinstance(risks['risks'], list):
                raise ValueError("Invalid risk assessment format")
            
            return risks
            
        except Exception as e:
            print(f"Error parsing risk assessment: {str(e)}")
            print(f"Raw response: {risk_text}")
            
            # Fallback risks if parsing fails
            return {
                "risks": [
                    "Financial data analysis incomplete - risk assessment limited",
                    "Market position analysis unavailable",
                    "Regulatory compliance status unknown"
                ]
            } 