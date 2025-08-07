from typing import Optional, Dict, List, Any
import re
from ..db.database import supabase
    
def search_cases(
    query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search for court cases based on text query and filter criteria.
    
    Args:
        query: Plain text search query (searches across multiple fields)
        jenis_kejahatan: Type of crime filter
        tahun: Year of case filter
        provinsi: Province code or name filter
        kabupaten: District/city name filter
        peradilan: Court name filter
        status_tahanan: Case status filter
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        Dictionary containing search results and metadata
    """
    try:
        # Build base query with all necessary joins
        base_query = supabase.table('putusan').select('''
            id,
            nomor_putusan,
            judul_putusan,
            jenis_kejahatan,
            lembaga_peradilan,
            tahun,
            tanggal_putusan:tanggal_dibacakan,
            lama_tahanan,
            status_tahanan,
            vonis_hukuman,
            hasil_putusan,
            kabupaten(
                nama_kabupaten,
                kode_provinsi,
                provinsi(nama_provinsi)
            )
        ''')
        
        # Apply text search query if provided
        if query and query.strip():
            # Search across multiple text fields including detail data
            search_query = f'%{query.strip()}%'
            base_query = base_query.or_(
                f'judul_putusan.ilike.{search_query},'
                f'hasil_putusan.ilike.{search_query},'
                f'nomor_putusan.ilike.{search_query},'
                f'jenis_kejahatan.ilike.{search_query},'
                f'lembaga_peradilan.ilike.{search_query},'
                f'status_tahanan.ilike.{search_query}'
            )
        
        # Get total count first (before pagination)
        count_query = base_query
        count_result = count_query.execute()
        total_count = len(count_result.data) if count_result.data else 0

        # print(f"results: {count_result.data}")
         
        # Apply pagination and ordering
        paginated_query = base_query.order('tanggal_dibacakan', desc=True).range(offset, offset + limit - 1)
        
        # Execute paginated query
        result = paginated_query.execute()
        
        # Process and format results
        processed_data = []
        for item in result.data if result.data else []:
            # Get detailed information from putusan_detail table
            detail_data = get_putusan_detail(item.get("nomor_putusan"))

            # print(f"Detail for {item.get('nomor_putusan')}: {detail_data}")
            
            # Format the case data
            formatted_item = {
                "id": item.get("id"),
                "nomor_putusan": item.get("nomor_putusan"),
                "judul_putusan": item.get("judul_putusan"),
                "jenis_kejahatan": item.get("jenis_kejahatan"),
                "lembaga_peradilan": item.get("lembaga_peradilan"),
                "tahun": item.get("tahun"),
                "tanggal_putusan": item.get("tanggal_putusan"),
                "status_tahanan": item.get("status_tahanan"),
                "lama_tahanan": item.get("lama_tahanan"),
                "vonis_hukuman": item.get("vonis_hukuman"),
                "hasil_putusan": item.get("hasil_putusan"),
                "lokasi": {
                    "kabupaten": item.get("kabupaten", {}).get("nama_kabupaten") if item.get("kabupaten") else None,
                    "provinsi": (
                        item.get("kabupaten", {}).get("provinsi", {}).get("nama_provinsi") 
                        if item.get("kabupaten") and item.get("kabupaten").get("provinsi") 
                        else None
                    ),
                    "kode_provinsi": item.get("kabupaten", {}).get("kode_provinsi") if item.get("kabupaten") else None
                },
                "pihak_terlibat": detail_data.get("pihak_terlibat", {})
            }
            processed_data.append(formatted_item)
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        current_page = (offset // limit) + 1
        
        return {
            "data": processed_data,
            "meta": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "page": current_page,
                "total_pages": total_pages,
                "has_next": offset + limit < total_count,
                "has_prev": offset > 0,
                "search_query": query,
                "filters_applied": {
                    "text_search": bool(query and query.strip()),
                }
            }
        }
    
    except Exception as e:
        raise Exception(f"Error searching cases: {str(e)}")

def mapping_putusan_detail(data_list, detail, table_name, column_name=None):
    if table_name != "hakim":
        result_data = detail.get(table_name)
        if isinstance(result_data, list):
            for item in result_data:
                if item.get(column_name):
                    data_list.append(item.get(column_name))
        elif isinstance(result_data, dict):
            if result_data.get(column_name):
                data_list.append(result_data.get(column_name))
    else:
        result_data = detail["hakim"]
        if isinstance(result_data, list):
            for hakim in result_data:
                if hakim.get("nama_hakim"):
                    hakim_info = {
                        "nama_hakim": hakim.get("nama_hakim", ""),
                        "jabatan": hakim.get("jabatan", ""),
                    }
                    data_list.append(hakim_info)
        elif isinstance(result_data, dict):
            if result_data.get("nama_hakim"):
                hakim_info = {
                    "nama_hakim": result_data.get("nama_hakim", ""),
                    "jabatan": result_data.get("jabatan", ""),
                }
                data_list.append(hakim_info)

def get_putusan_detail(nomor_putusan: str) -> Dict[str, Any]:
    """
    Get detailed information from putusan_detail table by nomor_putusan.
    
    Args:
        nomor_putusan: Case number to look up details
        
    Returns:
        Dictionary containing detailed case information
    """
    try:
        if not nomor_putusan:
            return {"pihak_terlibat": {}}
        
        # Query putusan_detail table
        # First, get the basic detail record to check which relations exist
        basic_detail = supabase.table('putusan_detail').select('id, terdakwa(nama_lengkap), hakim(nama_hakim), saksi(nama_saksi), penuntut_umum(nama_penuntut)').eq('nomor_putusan', nomor_putusan).execute()

        if not basic_detail.data:
            return {"pihak_terlibat": {}}
        
        detail_record = basic_detail.data[0]

        # print(f"Basic detail for {nomor_putusan}: {detail_record}")
        
        # Build select query dynamically based on which relations have values
        select_fields = []
        if detail_record.get('terdakwa'):
            select_fields.append('terdakwa(nama_terdakwa:nama_lengkap)')
        
        if detail_record.get('hakim'):
            select_fields.append('hakim(nama_hakim, jabatan)')
        
        if detail_record.get('saksi'):
            select_fields.append('saksi(nama_saksi)')
        
        if detail_record.get('penuntut_umum'):
            select_fields.append('penuntut_umum(nama_penuntut)')

        # print(f"Selected fields for {nomor_putusan}: {select_fields}")
        
        # If no relations have values, return empty result
        if not select_fields:
            detail_result = basic_detail
        else:
            # Query with only the relations that have values
            select_query = ', '.join(select_fields)
            # print(f"Executing detail query for {nomor_putusan} with fields: {select_query}")
            detail_result = supabase.table('putusan_detail').select(select_query).eq('nomor_putusan', nomor_putusan).execute()
        
        if not detail_result.data:
            return {"pihak_terlibat": {}}

        # Process the detail data
        detail = detail_result.data        
        terdakwa_list = []
        hakim_list = []
        saksi_list = []
        penuntut_list = []
        
        for item in detail:
            # Map terdakwa data
            if item.get("terdakwa"):
                mapping_putusan_detail(terdakwa_list, item, "terdakwa", "nama_terdakwa")
            # Map hakim data
            if item.get("hakim"):
                mapping_putusan_detail(hakim_list, item, "hakim")
            # Map saksi data
            if item.get("saksi"):
                mapping_putusan_detail(saksi_list, item, "saksi", "nama_saksi")
            # Map penuntut data
            if item.get("penuntut_umum"):
                mapping_putusan_detail(penuntut_list, item, "penuntut_umum", "nama_penuntut")
        
        # Build the complete pihak_terlibat response
        pihak_terlibat = {
            "terdakwa": terdakwa_list,
            "hakim": hakim_list,
            "saksi": saksi_list,
            "penuntut": penuntut_list
        }
        
        return {"pihak_terlibat": pihak_terlibat}
    
    except Exception as e:
        # if e.code != '42703':
        print(f"Error getting putusan detail for {nomor_putusan}: {str(e)}")
        return {"pihak_terlibat": {}}

def get_person_roles(person_name: str, pihak_terlibat: Dict) -> List[str]:
    """
    Get all roles a person has in a case.
    
    Args:
        person_name: Name to search for
        pihak_terlibat: Dictionary of involved parties
        
    Returns:
        List of roles the person has
    """
    roles = []
    person_lower = person_name.lower()
    
    for role, people in pihak_terlibat.items():
        if isinstance(people, list):
            for person in people:
                if person_lower in person.lower():
                    roles.append(role)
                    break
    
    return roles

def format_currency(amount: Any) -> str:
    """Format currency amount to readable string."""
    if not amount:
        return ""
    
    try:
        if isinstance(amount, str):
            # Extract numbers from string
            numbers = re.findall(r'\d+(?:\.\d+)?', amount)
            if numbers:
                amount = float(numbers[0])
            else:
                return amount
        
        if isinstance(amount, (int, float)):
            if amount >= 1_000_000_000:  # Billion
                return f"{amount/1_000_000_000:.1f} miliar Rupiah"
            elif amount >= 1_000_000:  # Million
                return f"{amount/1_000_000:.1f} juta Rupiah"
            elif amount >= 1_000:  # Thousand
                return f"{amount/1_000:.1f} ribu Rupiah"
            else:
                return f"{amount:,.0f} Rupiah"
        
        return str(amount)
    except:
        return str(amount) if amount else ""

def parse_person_list(person_data: Any) -> List[str]:
    """Parse person data into list of names."""
    if not person_data:
        return []
    
    if isinstance(person_data, str):
        # Split by common separators
        names = re.split(r'[,;]|\s+dan\s+|\s+&\s+', person_data)
        return [name.strip() for name in names if name.strip()]
    
    if isinstance(person_data, list):
        return [str(item).strip() for item in person_data if str(item).strip()]
    
    return [str(person_data).strip()]