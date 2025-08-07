from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
    
class HakimResponse(BaseModel):
    """Model for judge information."""
    nama_hakim: str = Field(..., description="Full name of judge")
    jabatan: str = Field(..., description="Position/title of judge")

# Model for involved parties
class PihakTerlibatResponse(BaseModel):
    """Model for all parties involved in a case."""
    terdakwa: List = Field(default=[], description="List of defendants")
    hakim: List[HakimResponse] = Field(default=[], description="List of judges")
    saksi: List = Field(default=[], description="List of witnesses")
    penuntut: List = Field(default=[], description="List of prosecutors")

# Model for location information
class LokasiResponse(BaseModel):
    """Model for location information."""
    kabupaten: Optional[str] = Field(None, description="District/city name")
    provinsi: Optional[str] = Field(None, description="Province name")
    kode_provinsi: Optional[str] = Field(None, description="Province code")

# Model for individual case data
class CaseResponse(BaseModel):
    """Model for individual case information."""
    id: str = Field(..., description="Case ID")
    nomor_putusan: str = Field(..., description="Case number")
    judul_putusan: str = Field(..., description="Case title")
    jenis_kejahatan: str = Field(..., description="Type of crime")
    lembaga_peradilan: str = Field(..., description="Court institution")
    tahun: int = Field(..., description="Year of case")
    tanggal_putusan: Optional[str] = Field(None, description="Date of verdict")
    status_tahanan: Optional[str] = Field(None, description="Detention status")
    lama_tahanan: Optional[str] = Field(None, description="Duration of detention")
    vonis_hukuman: Optional[str] = Field(None, description="Sentence/verdict")
    hasil_putusan: Optional[str] = Field(None, description="Case outcome")
    lokasi: LokasiResponse = Field(..., description="Location information")
    pihak_terlibat: PihakTerlibatResponse = Field(..., description="Involved parties")

# Model for search filters
class SearchFiltersResponse(BaseModel):
    """Model for applied search filters."""
    text_search: bool = Field(..., description="Whether text search was applied")
    jenis_kejahatan: Optional[str] = Field(None, description="Crime type filter")
    tahun: Optional[int] = Field(None, description="Year filter")
    provinsi: Optional[str] = Field(None, description="Province filter")
    kabupaten: Optional[str] = Field(None, description="District filter")
    peradilan: Optional[str] = Field(None, description="Court filter")
    status_tahanan: Optional[str] = Field(None, description="Detention status filter")

# Model for pagination metadata
class SearchMetaResponse(BaseModel):
    """Model for search metadata and pagination."""
    total: int = Field(..., description="Total number of results")
    limit: int = Field(..., description="Number of results per page")
    offset: int = Field(..., description="Number of results skipped")
    page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more results")
    has_prev: bool = Field(..., description="Whether there are previous results")
    search_query: Optional[str] = Field(None, description="Search query used")
    filters_applied: SearchFiltersResponse = Field(..., description="Filters that were applied")

# Main search response model
class SearchCasesResponse(BaseModel):
    """Main response model for case search."""
    data: List[CaseResponse] = Field(..., description="List of cases found")
    meta: SearchMetaResponse = Field(..., description="Search metadata and pagination")

# Model for person role information (used in person search)
class PersonRoleResponse(BaseModel):
    """Model for person role information."""
    role: str = Field(..., description="Role type (terdakwa, hakim, saksi, penuntut)")
    nama: str = Field(..., description="Person name")
    details: Dict[str, Any] = Field(default={}, description="Additional role details")

# Enhanced case response for person search
class PersonSearchCaseResponse(CaseResponse):
    """Extended case response that includes person role information."""
    person_roles: List[str] = Field(default=[], description="Roles the searched person has in this case")

# Model for person search metadata
class PersonSearchMetaResponse(BaseModel):
    """Model for person search metadata."""
    total: int = Field(..., description="Total number of cases found")
    limit: int = Field(..., description="Number of results per page")
    offset: int = Field(..., description="Number of results skipped")
    search_person: str = Field(..., description="Person name searched for")
    person_type: Optional[str] = Field(None, description="Person type filter applied")
    found_in_cases: int = Field(..., description="Number of cases where person was found")

# Person search response model
class PersonSearchResponse(BaseModel):
    """Response model for person-based case search."""
    data: List[PersonSearchCaseResponse] = Field(..., description="List of cases where person was found")
    meta: PersonSearchMetaResponse = Field(..., description="Person search metadata")

# Model for case detail response
class CaseDetailResponse(BaseModel):
    """Model for detailed case information."""
    data: Dict[str, Any] = Field(..., description="Complete case data")
    meta: Dict[str, Any] = Field(..., description="Retrieval metadata")

# Model for search suggestions
class SearchSuggestionsResponse(BaseModel):
    """Model for search suggestions."""
    suggestions: List[str] = Field(..., description="List of search suggestions")
    count: int = Field(..., description="Number of suggestions returned")

class SearchSuggestionsMetaResponse(BaseModel):
    """Model for search suggestions metadata."""
    query: str = Field(..., description="Query used for suggestions")
    limit: int = Field(..., description="Maximum suggestions requested")

class SuggestionsResponse(BaseModel):
    """Main response model for search suggestions."""
    data: SearchSuggestionsResponse = Field(..., description="Suggestion data")
    meta: SearchSuggestionsMetaResponse = Field(..., description="Suggestion metadata")

# Model for statistics response
class StatisticsOverviewResponse(BaseModel):
    """Model for statistics overview."""
    total_cases: int = Field(..., description="Total number of cases")
    recent_cases_30_days: int = Field(..., description="Cases in last 30 days")

class StatisticsDistributionsResponse(BaseModel):
    """Model for statistics distributions."""
    by_crime_type: Dict[str, int] = Field(..., description="Cases by crime type")
    by_year: Dict[str, int] = Field(..., description="Cases by year")
    by_status: Dict[str, int] = Field(..., description="Cases by status")
    by_province: Dict[str, int] = Field(..., description="Cases by province")

class StatisticsDataResponse(BaseModel):
    """Model for statistics data."""
    overview: StatisticsOverviewResponse = Field(..., description="Overview statistics")
    distributions: StatisticsDistributionsResponse = Field(..., description="Distribution statistics")

class StatisticsMetaResponse(BaseModel):
    """Model for statistics metadata."""
    generated_at: str = Field(..., description="When statistics were generated")
    data_freshness: str = Field(..., description="Data freshness indicator")

class StatisticsResponse(BaseModel):
    """Main response model for statistics."""
    data: StatisticsDataResponse = Field(..., description="Statistics data")
    meta: StatisticsMetaResponse = Field(..., description="Statistics metadata")

# Generic API response wrapper (for compatibility with existing APIResponse)
class SearchAPIResponse(BaseModel):
    """Generic API response wrapper for search endpoints."""
    data: Any = Field(..., description="Response data")
    meta: Any = Field(..., description="Response metadata")
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "data": [],
                "meta": {
                    "total": 0,
                    "limit": 50,
                    "offset": 0,
                    "page": 1,
                    "total_pages": 0
                }
            }
        }