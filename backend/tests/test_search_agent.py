import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

import asyncio
import pytest
from app.agents.search import SearchAgent
from app.core.config import get_settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search_agent():
    """Test the search agent with a known company."""
    try:
        # Initialize the search agent
        agent = SearchAgent()
        logger.info("SearchAgent initialized")

        # Test company
        company_name = "Apple"
        search_plan = {
            "financial_metrics": ["Revenue", "Profit", "Growth"],
            "market_analysis": ["Market Share", "Competition"],
            "risk_factors": ["Market Risk", "Operational Risk"]
        }

        logger.info(f"Testing search for company: {company_name}")
        
        # Execute the search
        result = await agent.process(company_name, search_plan)
        
        # Log the results
        logger.info("Search completed successfully")
        logger.info(f"Company Info: {result.get('company_info', {})}")
        logger.info(f"Financial Data: {result.get('financial_data', {})}")
        logger.info(f"Market Data: {result.get('market_data', {})}")
        logger.info(f"News Data Count: {len(result.get('news_data', []))}")

        # Basic assertions
        assert result is not None, "Result should not be None"
        assert 'company_info' in result, "Result should contain company_info"
        assert 'financial_data' in result, "Result should contain financial_data"
        assert 'market_data' in result, "Result should contain market_data"
        assert 'news_data' in result, "Result should contain news_data"

        # Check for required fields
        company_info = result['company_info']
        assert company_info['name'] == company_name, "Company name should match"
        assert company_info['description'] is not None, "Description should not be None"
        assert company_info['sector'] is not None, "Sector should not be None"
        assert company_info['industry'] is not None, "Industry should not be None"

        # Check financial data
        financial_data = result['financial_data']
        required_fields = ['price', 'change_percent', 'volume']
        for field in required_fields:
            assert field in financial_data, f"Financial data should contain {field}"
            assert financial_data[field] is not None, f"{field} should not be None"
            assert financial_data[field] != 0, f"{field} should not be 0"

        logger.info("All assertions passed successfully")
        return result

    except Exception as e:
        logger.error(f"Error in test_search_agent: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    # Run the test
    try:
        logger.info("Starting search agent test")
        result = asyncio.run(test_search_agent())
        logger.info("Test completed successfully")
        
        # Print detailed results
        print("\nDetailed Results:")
        print("================")
        print(f"\nCompany Info:")
        for key, value in result['company_info'].items():
            print(f"{key}: {value}")
        
        print("\nKey Financial Metrics:")
        financial_metrics = [
            'price', 'change_percent', 'volume', 'market_cap',
            'pe_ratio', 'revenue', 'gross_profit', 'operating_margin'
        ]
        for metric in financial_metrics:
            print(f"{metric}: {result['financial_data'].get(metric, 'N/A')}")
        
        print("\nLatest News:")
        for news in result['news_data'][:3]:  # Show first 3 news items
            print(f"\nTitle: {news['title']}")
            print(f"Published: {news['publishedAt']}")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        raise 