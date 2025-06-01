from .base import BaseAgent
from typing import Dict, Any, List

class ReportAgent(BaseAgent):
    async def process(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        risk_assessment: List[str]
    ) -> Dict[str, Any]:
        """Generate the final company analysis report."""
        system_message = """You are a financial report writer. Create a clear, concise report summarizing the company 
        analysis. Focus on key insights and present them in a way that's easy to understand."""
        
        # Prepare data for report generation
        report_input = {
            "company_info": company_data["company_info"],
            "financial_data": company_data["financial_data"],
            "market_data": company_data["market_data"],
            "news_data": company_data["news_data"],
            "financial_analysis": financial_analysis,
            "risks": risk_assessment
        }
        
        prompt = f"""Create a comprehensive report for {company_name} using the following data:
        
        Company Information:
        {report_input['company_info']}
        
        Financial Analysis:
        {report_input['financial_analysis']}
        
        Risk Assessment:
        {report_input['risks']}
        
        Recent News:
        {[article["title"] for article in report_input['news_data']]}
        
        Generate a report in JSON format with the following structure:
        {{
            "company_name": "string",
            "overview": "comprehensive overview paragraph",
            "financial_metrics": {{
                "revenue": "string with formatting",
                "net_income": "string with formatting",
                "total_debt": "string with formatting",
                "cash": "string with formatting"
            }},
            "potential_risks": ["array of risk statements"],
            "sources": ["array of source citations"]
        }}
        
        Format financial numbers in billions/millions (e.g., "$94 billion", "$15 million").
        Include relevant sources from news articles and financial data.
        """
        
        report_text = await self._get_completion(prompt, system_message)
        
        try:
            import json
            report = json.loads(report_text)
            
            # Ensure all required fields are present
            required_fields = {
                "company_name": company_name,
                "overview": "Overview not available due to processing error",
                "financial_metrics": report_input["financial_data"],
                "potential_risks": risk_assessment,
                "sources": [article["url"] for article in report_input["news_data"]]
            }
            
            for field, default_value in required_fields.items():
                if field not in report:
                    report[field] = default_value
            
            return report
            
        except:
            # Fallback report if parsing fails
            return {
                "company_name": company_name,
                "overview": "Report generation failed. Please try again later.",
                "financial_metrics": report_input["financial_data"],
                "potential_risks": risk_assessment,
                "sources": [article["url"] for article in report_input["news_data"]]
            } 