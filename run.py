#!/usr/bin/env python3
"""
Production server startup script
"""
import uvicorn
import os
from app.core.config import settings

if __name__ == "__main__":
    # Production configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 1)),
        log_level="info",
        access_log=True,
        reload=settings.debug
    )