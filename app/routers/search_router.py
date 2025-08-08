from fastapi import APIRouter
from typing import Optional
from fastapi import Query, HTTPException
from ..responses.search_response import  SearchCasesResponse
from ..services.search_service import search_cases

router = APIRouter(prefix="/api", tags=["cluster"])
@router.get("/search", response_model=SearchCasesResponse)
async def search_court_cases(
    query: Optional[str] = Query(None, description="Text search query (searches in case titles, defendants, prosecutors, etc.)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination")
):
    """
    Search for court cases using plain text query and filters.
    
    **Text Search:**
    - Searches across case titles, case summaries, defendant names, prosecutor names, and case numbers
    - Use simple keywords or phrases (e.g., "korupsi bantuan sosial", "Budi Santoso")
    
    **Available Filters:**
    - Crime type: Filter by specific crime categories
    - Year: Filter by case year
    - Location: Filter by province or district
    - Court: Filter by specific court
    - Status: Filter by case status
    
    **Examples:**
    - `/api/search/cases?query=korupsi` - Search for corruption cases
    - `/api/search/cases?query=Budi Santoso` - Search for cases involving Budi Santoso
    - `/api/search/cases?jenis_kejahatan=Korupsi&tahun=2024` - Filter corruption cases from 2024
    """
    try:
        result = search_cases(
            query=query,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))