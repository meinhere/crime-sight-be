"""
API routers module.

Contains all FastAPI route handlers organized by functionality.
"""

from .cluster_router import router as cluster_router
from .search_router import router as search_router

# Uncomment when implementing these routers
# from .users_router import router as users_router
# from .items_router import router as items_router

__all__ = ["cluster_router", "search_router"]