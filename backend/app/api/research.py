from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..agents.manager import ManagerAgent
import traceback

router = APIRouter()

class CompanyRequest(BaseModel):
    company_name: str

class CompanyResponse(BaseModel):
    company_name: str
    overview: str
    financial_metrics: dict
    potential_risks: list[str]
    sources: list[str]

@router.post("/analyze", response_model=CompanyResponse)
async def analyze_company(request: CompanyRequest):
    try:
        manager = ManagerAgent()
        result = await manager.process(request.company_name)
        return result
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Detailed error: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing company: {str(e)}\nTrace: {error_trace}"
        ) 