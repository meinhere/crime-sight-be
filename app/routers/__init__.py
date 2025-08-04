"""
API routers module.

Contains FastAPI routers for different endpoints.
"""

from .cluster_router import router as cluster_router

# Import other routers when they are implemented
# from .find import router as find_router
# from .scrap import router as scrap_router
# from .summarize import router as summarize_router
# from .trend import router as trend_router

__all__ = ["cluster_router"]