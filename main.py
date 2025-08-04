"""
Main entry point for the Crime Sight Backend API.
This script can be run directly from the project root.
"""

if __name__ == "__main__":
    from app.main import app
    import uvicorn
    import os
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)
