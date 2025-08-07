import time
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services.scrap_service import get_all_links, process_putusan

router = APIRouter(prefix="/api", tags=["cluster"])
@router.get("/scrap")
async def get_scrap_data(
    base_url: str = Query(
        "https://putusan3.mahkamahagung.go.id/direktori/index/pengadilan/pn-bandung/kategori/pidana-umum-1",
        description="Base URL untuk scraping data putusan"
    ),
):
    # 1. Ambil semua link putusan
    links = get_all_links(base_url, 1, 5)
    print(f"Total {len(links)} putusan ditemukan.")

    # 2. Proses setiap putusan
    for idx, link in enumerate(links):
        print(f"{idx + 1}. ", end="")
        process_putusan(link)

        # if result == None:
        #   break

        time.sleep(2)  # Delay untuk hindari rate limiting