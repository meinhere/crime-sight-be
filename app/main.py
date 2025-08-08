import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Handle both relative and absolute imports for flexibility
try:
    # Try relative import (when run as module)
    from .routers.master_router import router as master_router
    from .routers.cluster_router import router as cluster_router
    from .routers.search_router import router as search_router
    from .routers.trend_router import router as trend_router
    # from .routers.scrap_router import router as scrap_router
    # from .routers.summarize_router import router as summarize_router
except ImportError:
    # Fallback to absolute import (when run directly)
    # Add the parent directory to sys.path to resolve absolute imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.routers.master_router import router as master_router
    from app.routers.cluster_router import router as cluster_router
    from app.routers.search_router import router as search_router
    from app.routers.trend_router import router as trend_router
    # from app.routers.scrap_router import router as scrap_router
    # from app.routers.summarize_router import router as summarize_router

app = FastAPI(
    title="Crime Sight API",
    description="Backend API for Crime Sight application",
    version="1.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(master_router)
app.include_router(cluster_router)
app.include_router(search_router)
app.include_router(trend_router)
# app.include_router(scrap_router)
# app.include_router(summarize_router)

@app.get("/")
async def root():
    return {"message": "Crime Sight API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)