from pydantic import BaseModel, Field
from typing import List, Optional
    
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

# Main search response model
class SearchCasesResponse(BaseModel):
    """Main response model for case search."""
    data: List[CaseResponse] = Field(..., description="List of cases found")
    meta: SearchMetaResponse = Field(..., description="Search metadata and pagination")
