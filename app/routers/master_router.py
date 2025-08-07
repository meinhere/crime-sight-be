from fastapi import APIRouter, HTTPException
from ..db.database import supabase

router = APIRouter(prefix="/api/master", tags=["master-data"])

@router.get("/jenis-kejahatan")
async def get_jenis_kejahatan():
    """
    Get list of unique crime types (jenis kejahatan) from putusan table.
    
    **Returns:**
    Simple list of unique crime types.
    
    **Example:**
    - `/api/master/jenis-kejahatan` - Get all unique crime types
    """
    try:
        # Get all jenis_kejahatan from putusan table
        result = supabase.table('putusan').select('jenis_kejahatan').execute()
        
        if not result.data:
            return []
        
        # Get unique crime types
        crime_types = set()
        for item in result.data:
            crime_type = item.get('jenis_kejahatan')
            if crime_type and crime_type.strip():
                crime_types.add(crime_type.strip())
        
        # Convert to sorted list
        return sorted(list(crime_types))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving crime types: {str(e)}")

@router.get("/provinsi")
async def get_provinsi():
    """
    Get list of unique provinces from putusan table.
    
    **Returns:**
    Simple list of unique province names.
    
    **Example:**
    - `/api/master/provinsi` - Get all unique provinces
    """
    try:
        # Get all cases with provinsi data
        result = supabase.table('putusan').select('''
            kabupaten(
                provinsi(kode_provinsi, nama_provinsi)
            )
        ''').execute()
        
        if not result.data:
            return []
        
        # Extract unique provinces with their codes
        provinces_dict = {}
        
        for item in result.data:
            kabupaten = item.get('kabupaten')
            if kabupaten:
              provinsi_info = kabupaten.get('provinsi')
              if provinsi_info and provinsi_info.get('nama_provinsi') and provinsi_info.get('kode_provinsi'):
                  kode = provinsi_info.get('kode_provinsi')
                  nama = provinsi_info.get('nama_provinsi')
                  provinces_dict[kode] = {'kode_provinsi': kode, 'nama_provinsi': nama}
        
        # Convert to sorted list by nama_provinsi
        return sorted(list(provinces_dict.values()), key=lambda x: x['nama_provinsi'])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving provinces: {str(e)}")

@router.get("/tahun")
async def get_available_years():
    """
    Get list of available years from putusan table.
    
    **Returns:**
    Simple list of years, sorted descending.
    
    **Example:**
    - `/api/master/years` - Get all available years
    """
    try:
        result = supabase.table('putusan').select('tahun').execute()
        
        if not result.data:
            return []
        
        # Get unique years
        years = set()
        for item in result.data:
            year = item.get('tahun')
            if year:
                years.add(year)
        
        # Convert to sorted list (descending)
        return sorted(list(years), reverse=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving years: {str(e)}")