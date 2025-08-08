from pydantic import BaseModel
from typing import List

# Base Models for Master Data
class ProvinsiData(BaseModel):
    """Model for province data with code and name"""
    kode_provinsi: str
    nama_provinsi: str

# Response Models for Each Endpoint
class JenisKejahatanResponse(BaseModel):
    """Response model for /api/master/jenis-kejahatan endpoint"""
    data: List[str]

class ProvinsiResponse(BaseModel):
    """Response model for /api/master/provinsi endpoint"""
    data: List[ProvinsiData]

class TahunResponse(BaseModel):
    """Response model for /api/master/tahun endpoint"""
    data: List[int]
