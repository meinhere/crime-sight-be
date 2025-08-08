from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from ..db.database import supabase
from ..responses.trend_response import TrendResponse
from ..services.trend_service import calculate_stats

router = APIRouter(prefix="/api", tags=["trends"])

@router.get("/trends", response_model=TrendResponse)
async def get_crime_trends(
    start_year: Optional[int] = Query(None, description="Start year for trend analysis"),
    end_year: Optional[int] = Query(None, description="End year for trend analysis"),
    provinsi: Optional[str] = Query(None, description="Province code filter")
):
    """
    Get comprehensive crime trend analysis with statistics.
    
    **Parameters:**
    - `start_year`: Starting year for analysis (optional, defaults to earliest year in data)
    - `end_year`: Ending year for analysis (optional, defaults to current year)
    - `provinsi`: Province code filter (optional)
    
    **Returns:**
    Comprehensive trend data including:
    - Time series data by year
    - Crime type trends
    - Time of occurrence trends
    - Location trends
    - Regional trends
    - Statistical analysis (highest, lowest, averages)
    
    **Examples:**
    - `/api/trends` - Get all trends
    - `/api/trends?start_year=2020&end_year=2023` - Get trends for specific period
    - `/api/trends?provinsi=32` - Get trends for West Java province
    """
    try:
        # 1. Get start year from database if not provided
        if not start_year:
            start_year_result = supabase.table('putusan').select('tahun').order('tahun', desc=False).limit(1).execute()
            start_year = start_year_result.data[0]['tahun'] if start_year_result.data else 2000
        
        # Set end year to current year if not provided
        if not end_year:
            end_year = datetime.now().year

        # 2. Build query with filters
        query = supabase.table('putusan').select('''
            id,
            tahun,
            jenis_kejahatan,
            waktu_kejadian(waktu_kejadian),
            lokasi_kejadian(nama_lokasi),
            kabupaten(
                nama_kabupaten,
                kode_provinsi,
                provinsi(nama_provinsi)
            )
        ''')

        # Apply year range filter
        query = query.gte('tahun', start_year).lte('tahun', end_year)

        # Apply province filter if provided
        if provinsi:
            query = query.eq('kabupaten.kode_provinsi', provinsi)

        # 3. Execute query
        result = query.execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")

        data = result.data

        # 4. Generate labels for years
        labels = [str(year) for year in range(start_year, end_year + 1)]

        # 5. Process datasets for crime types (jenis kejahatan)
        jenis_kejahatan_list = list(set([
            item['jenis_kejahatan'] for item in data 
            if item.get('jenis_kejahatan')
        ]))

        jenis_kejahatan_datasets = []
        for jenis in jenis_kejahatan_list:
            trend_data = []
            for year in labels:
                count = len([
                    item for item in data 
                    if str(item['tahun']) == year and item['jenis_kejahatan'] == jenis
                ])
                trend_data.append(count)
            
            jenis_kejahatan_datasets.append({
                "label": jenis,
                "data": trend_data
            })

        # 6. Process datasets for time of occurrence (waktu kejadian)
        waktu_kejadian_list = list(set([
            item['waktu_kejadian']['waktu_kejadian'] for item in data 
            if item.get('waktu_kejadian') and item['waktu_kejadian'].get('waktu_kejadian')
        ]))

        waktu_kejadian_datasets = []
        for waktu in waktu_kejadian_list:
            trend_data = []
            for year in labels:
                count = len([
                    item for item in data 
                    if (str(item['tahun']) == year and 
                        item.get('waktu_kejadian') and 
                        item['waktu_kejadian'].get('waktu_kejadian') == waktu)
                ])
                trend_data.append(count)
            
            waktu_kejadian_datasets.append({
                "label": waktu,
                "data": trend_data
            })

        # 7. Process datasets for location (lokasi kejadian)
        lokasi_kejadian_list = list(set([
            item['lokasi_kejadian']['nama_lokasi'] for item in data 
            if item.get('lokasi_kejadian') and item['lokasi_kejadian'].get('nama_lokasi')
        ]))

        lokasi_kejadian_datasets = []
        for lokasi in lokasi_kejadian_list:
            trend_data = []
            for year in labels:
                count = len([
                    item for item in data 
                    if (str(item['tahun']) == year and 
                        item.get('lokasi_kejadian') and 
                        item['lokasi_kejadian'].get('nama_lokasi') == lokasi)
                ])
                trend_data.append(count)
            
            lokasi_kejadian_datasets.append({
                "label": lokasi,
                "data": trend_data
            })

        # 8. Process datasets for regions (wilayah)
        wilayah_datasets = []
        if provinsi:
            # If province is selected, show kabupaten data within that province
            kabupaten_list = list(set([
                item['kabupaten']['nama_kabupaten'] for item in data 
                if item.get('kabupaten') and item['kabupaten'].get('nama_kabupaten')
            ]))
            
            for kab in kabupaten_list:
                trend_data = []
                for year in labels:
                    count = len([
                        item for item in data 
                        if (str(item['tahun']) == year and 
                            item.get('kabupaten') and 
                            item['kabupaten'].get('nama_kabupaten') == kab)
                    ])
                    trend_data.append(count)
                
                wilayah_datasets.append({
                    "label": kab,
                    "data": trend_data
                })
        else:
            # If no province selected, show province data
            provinsi_list = list(set([
                item['kabupaten']['provinsi']['nama_provinsi'] for item in data 
                if (item.get('kabupaten') and 
                    item['kabupaten'].get('provinsi') and 
                    item['kabupaten']['provinsi'].get('nama_provinsi'))
            ]))
            
            for prov in provinsi_list:
                trend_data = []
                for year in labels:
                    count = len([
                        item for item in data 
                        if (str(item['tahun']) == year and 
                            item.get('kabupaten') and 
                            item['kabupaten'].get('provinsi') and 
                            item['kabupaten']['provinsi'].get('nama_provinsi') == prov)
                    ])
                    trend_data.append(count)
                
                wilayah_datasets.append({
                    "label": prov,
                    "data": trend_data
                })

        # 9. Calculate statistics
        total_records = len(data)

        # Cases by type
        cases_by_type = {}
        for jenis in jenis_kejahatan_list:
            cases_by_type[jenis] = len([
                item for item in data if item['jenis_kejahatan'] == jenis
            ])

        # Cases by waktu
        cases_by_waktu = {}
        for waktu in waktu_kejadian_list:
            cases_by_waktu[waktu] = len([
                item for item in data 
                if (item.get('waktu_kejadian') and 
                    item['waktu_kejadian'].get('waktu_kejadian') == waktu)
            ])

        # Cases by lokasi
        cases_by_lokasi = {}
        for lokasi in lokasi_kejadian_list:
            cases_by_lokasi[lokasi] = len([
                item for item in data 
                if (item.get('lokasi_kejadian') and 
                    item['lokasi_kejadian'].get('nama_lokasi') == lokasi)
            ])

        # Cases by wilayah
        cases_by_wilayah = {}
        if provinsi:
            kabupaten_list = list(set([
                item['kabupaten']['nama_kabupaten'] for item in data 
                if item.get('kabupaten') and item['kabupaten'].get('nama_kabupaten')
            ]))
            for kab in kabupaten_list:
                cases_by_wilayah[kab] = len([
                    item for item in data 
                    if (item.get('kabupaten') and 
                        item['kabupaten'].get('nama_kabupaten') == kab)
                ])
        else:
            provinsi_list = list(set([
                item['kabupaten']['provinsi']['nama_provinsi'] for item in data 
                if (item.get('kabupaten') and 
                    item['kabupaten'].get('provinsi') and 
                    item['kabupaten']['provinsi'].get('nama_provinsi'))
            ]))
            for prov in provinsi_list:
                cases_by_wilayah[prov] = len([
                    item for item in data 
                    if (item.get('kabupaten') and 
                        item['kabupaten'].get('provinsi') and 
                        item['kabupaten']['provinsi'].get('nama_provinsi') == prov)
                ])

        # Cases by year
        cases_by_year = []
        for year in labels:
            count = len([item for item in data if str(item['tahun']) == year])
            cases_by_year.append(count)

        # Year statistics
        year_stats = {
            "tertinggi": {"tahun": "", "jumlah": 0},
            "terendah": {"tahun": "", "jumlah": float('inf')},
            "rata_rata": 0
        }

        for i, count in enumerate(cases_by_year):
            year = labels[i]
            if count > year_stats["tertinggi"]["jumlah"]:
                year_stats["tertinggi"] = {"tahun": year, "jumlah": count}
            if count < year_stats["terendah"]["jumlah"]:
                year_stats["terendah"] = {"tahun": year, "jumlah": count}

        if year_stats["terendah"]["jumlah"] == float('inf'):
            year_stats["terendah"] = {"tahun": "", "jumlah": 0}

        total_cases_all_years = sum(cases_by_year)
        year_stats["rata_rata"] = round(total_cases_all_years / len(cases_by_year), 2) if cases_by_year else 0

        # Statistics for other categories using calculate_stats function
        type_stats = calculate_stats(cases_by_type)
        waktu_stats = calculate_stats(cases_by_waktu)
        lokasi_stats = calculate_stats(cases_by_lokasi)
        wilayah_stats = calculate_stats(cases_by_wilayah)

        # 10. Build response using Pydantic models structure
        trend_response = TrendResponse(
            meta={
                "total_records": total_records,
                "labels": labels,
                "details": {
                    "jenis_kejahatan": cases_by_type,
                    "waktu_kejadian": cases_by_waktu,
                    "lokasi_kejadian": cases_by_lokasi,
                    "wilayah": cases_by_wilayah
                },
                "statistics": {
                    "tahun": {
                        "tertinggi": {
                            "tahun": year_stats["tertinggi"]["tahun"],
                            "jumlah": year_stats["tertinggi"]["jumlah"]
                        },
                        "terendah": {
                            "tahun": year_stats["terendah"]["tahun"],
                            "jumlah": year_stats["terendah"]["jumlah"]
                        },
                        "rata_rata": year_stats["rata_rata"]
                    },
                    "jenis_kejahatan": {
                        "tertinggi": {
                            "jenis": type_stats["tertinggi"]["nama"],
                            "jumlah": type_stats["tertinggi"]["jumlah"]
                        },
                        "terendah": {
                            "jenis": type_stats["terendah"]["nama"],
                            "jumlah": type_stats["terendah"]["jumlah"]
                        },
                        "rata_rata": type_stats["rata_rata"]
                    },
                    "waktu_kejadian": {
                        "tertinggi": {
                            "waktu": waktu_stats["tertinggi"]["nama"],
                            "jumlah": waktu_stats["tertinggi"]["jumlah"]
                        },
                        "terendah": {
                            "waktu": waktu_stats["terendah"]["nama"],
                            "jumlah": waktu_stats["terendah"]["jumlah"]
                        },
                        "rata_rata": waktu_stats["rata_rata"]
                    },
                    "lokasi_kejadian": {
                        "tertinggi": {
                            "lokasi": lokasi_stats["tertinggi"]["nama"],
                            "jumlah": lokasi_stats["tertinggi"]["jumlah"]
                        },
                        "terendah": {
                            "lokasi": lokasi_stats["terendah"]["nama"],
                            "jumlah": lokasi_stats["terendah"]["jumlah"]
                        },
                        "rata_rata": lokasi_stats["rata_rata"]
                    },
                    "wilayah": {
                        "tertinggi": {
                            "wilayah": wilayah_stats["tertinggi"]["nama"],
                            "jumlah": wilayah_stats["tertinggi"]["jumlah"]
                        },
                        "terendah": {
                            "wilayah": wilayah_stats["terendah"]["nama"],
                            "jumlah": wilayah_stats["terendah"]["jumlah"]
                        },
                        "rata_rata": wilayah_stats["rata_rata"]
                    }
                },
                "filters": {
                    "provinsi": provinsi or "Semua Provinsi",
                    "tahun": f"{start_year}-{end_year}"
                }
            },
            data={
                "tahun": cases_by_year,
                "jenis_kejahatan": jenis_kejahatan_datasets,
                "waktu_kejadian": waktu_kejadian_datasets,
                "lokasi_kejadian": lokasi_kejadian_datasets,
                "wilayah": wilayah_datasets
            }
        )

        return trend_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trend data: {str(e)}")