"""
Routers module.

Contains all API route definitions.
"""

from . import cluster_router, search_router, master_router, trend_router

__all__ = ["cluster_router", "search_router", "master_router", "trend_router"]