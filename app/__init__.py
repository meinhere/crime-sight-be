"""
Crime Sight Backend Application

This package contains the FastAPI backend for the Crime Sight application,
providing APIs for crime data analysis, clustering, and visualization.
"""

from .dependencies import extract_url_document, extract_local_document

__version__ = "1.0.0"
__all__ = ["extract_url_document", "extract_local_document"]
