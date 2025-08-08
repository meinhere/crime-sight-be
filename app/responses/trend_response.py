from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Statistics Models
class YearStatistic(BaseModel):
    tahun: str
    jumlah: int

class CategoryStatistic(BaseModel):
    nama: str
    jumlah: int

class JenisKejahatanStatistic(BaseModel):
    jenis: str
    jumlah: int

class WaktuKejahatanStatistic(BaseModel):
    waktu: str
    jumlah: int

class LokasiKejahatanStatistic(BaseModel):
    lokasi: str
    jumlah: int

class WilayahStatistic(BaseModel):
    wilayah: str
    jumlah: int

class YearStats(BaseModel):
    tertinggi: YearStatistic
    terendah: YearStatistic
    rata_rata: float

class JenisKejahatanStats(BaseModel):
    tertinggi: JenisKejahatanStatistic
    terendah: JenisKejahatanStatistic
    rata_rata: float

class WaktuKejahatanStats(BaseModel):
    tertinggi: WaktuKejahatanStatistic
    terendah: WaktuKejahatanStatistic
    rata_rata: float

class LokasiKejahatanStats(BaseModel):
    tertinggi: LokasiKejahatanStatistic
    terendah: LokasiKejahatanStatistic
    rata_rata: float

class WilayahStats(BaseModel):
    tertinggi: WilayahStatistic
    terendah: WilayahStatistic
    rata_rata: float

class TrendStatistics(BaseModel):
    tahun: YearStats
    jenis_kejahatan: JenisKejahatanStats
    waktu_kejadian: WaktuKejahatanStats
    lokasi_kejadian: LokasiKejahatanStats
    wilayah: WilayahStats

# Dataset Models
class TrendDataset(BaseModel):
    label: str
    data: List[int]

# Details Models
class TrendDetails(BaseModel):
    jenis_kejahatan: Dict[str, int]
    waktu_kejadian: Dict[str, int]
    lokasi_kejadian: Dict[str, int]
    wilayah: Dict[str, int]

# Filters Model
class TrendFilters(BaseModel):
    provinsi: str
    tahun: str

# Meta Model
class TrendMeta(BaseModel):
    total_records: int
    labels: List[str]
    details: TrendDetails
    statistics: TrendStatistics
    filters: TrendFilters

# Data Model
class TrendData(BaseModel):
    tahun: List[int]
    jenis_kejahatan: List[TrendDataset]
    waktu_kejadian: List[TrendDataset]
    lokasi_kejadian: List[TrendDataset]
    wilayah: List[TrendDataset]

# Main Response Model
class TrendResponse(BaseModel):
    meta: TrendMeta
    data: TrendData