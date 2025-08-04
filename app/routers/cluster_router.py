from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..db.database import supabase
from ..responses.cluster_response import APIResponse
from ..services.cluster_service import group_and_count, perform_clustering

router = APIRouter(prefix="/api", tags=["cluster"])
@router.get("/cluster", response_model=APIResponse)
async def get_crime_clusters(
    jenis_kejahatan: Optional[str] = Query(None),
    tahun: Optional[int] = Query(None),
    provinsi: Optional[str] = Query(None)
):
    try:
        # 1. Build query
        query = supabase.table('putusan').select('id, jenis_kejahatan, tahun, kabupaten(nama_kabupaten, kode_provinsi)')
        
        if jenis_kejahatan:
            query = query.eq('jenis_kejahatan', jenis_kejahatan)
        if tahun:
            query = query.eq('tahun', tahun)
        if provinsi:
            query = query.eq('kabupaten.kode_provinsi', provinsi)

        # 2. Execute query
        res = query.execute()
        # print(f"Raw query result: {res.data if res.data else 'No data'}")  # Debug: show first 2 items
        
        data = [item for item in res.data if item and isinstance(item, dict) and item.get('kabupaten') is not None]
        # print(f"Filtered data count: {len(data)}")
        # if data:
        #     print(f"Sample filtered item: {data[0]}")
        
        if not data:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")

        # 3. Process data
        group_col = 'kabupaten.nama_kabupaten'
        # print(f"Group column: {group_col}")
        grouped_data = group_and_count(data, group_col)
        # print(f"Grouped data: {grouped_data}")
        clustered_data = perform_clustering(grouped_data)

        # 4. Prepare response
        response = {
            "data": clustered_data,
            "meta": {
                "total_records": len(data),
                "filters": {
                    "jenis_kejahatan": jenis_kejahatan,
                    "tahun": tahun,
                    "provinsi": provinsi
                }
            }
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))