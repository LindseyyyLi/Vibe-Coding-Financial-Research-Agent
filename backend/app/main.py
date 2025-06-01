from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .agents.manager import ManagerAgent
import logging
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=300.0)  # 5 minutes timeout
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={"detail": "Request timeout. The operation took too long to complete."}
            )

app = FastAPI(title="Financial Research Assistant API")

# Add timeout middleware
app.add_middleware(TimeoutMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Initialize the manager agent
manager = ManagerAgent()

class CompanyRequest(BaseModel):
    company_name: str

class CompanyResponse(BaseModel):
    company_name: str
    overview: str
    financial_metrics: Dict[str, Any]
    potential_risks: List[str]
    sources: List[str]

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} request to {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Request completed with status code {response.status_code}")
        return response
    except asyncio.TimeoutError:
        logger.error("Request timed out")
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timeout. The operation took too long to complete."}
        )
    except Exception as e:
        logger.error(f"Request failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": {"error": "Internal server error", "message": str(e)}}
        )

@app.get("/")
async def root():
    return {"status": "ok", "message": "Financial Research Assistant API is running"}

@app.post("/api/research", response_model=CompanyResponse)
async def research_company(request: CompanyRequest):
    logger.info(f"Received research request for company: {request.company_name}")
    try:
        result = await asyncio.wait_for(
            manager.process(request.company_name),
            timeout=240.0  # 4 minutes timeout for processing
        )
        if not result.get("company_name"):
            raise ValueError("Failed to get company data")
        logger.info(f"Successfully processed research for {request.company_name}")
        return result
    except asyncio.TimeoutError:
        logger.error(f"Research processing timed out for {request.company_name}")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Processing timeout",
                "message": "The research operation took too long to complete. Please try again."
            }
        )
    except Exception as e:
        logger.error(f"Failed to process company research: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to process company research",
                "message": str(e)
            }
        )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is operational"} 