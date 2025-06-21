from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.routers import users, agents, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Full stack FastAPI and MongoDB application following best practices",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with proper API versioning
    application.include_router(
        auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"]
    )

    application.include_router(
        users.router, prefix=f"{settings.api_v1_prefix}/users", tags=["Users"]
    )

    application.include_router(
        agents.router, prefix=f"{settings.api_v1_prefix}/agents", tags=["Agents"]
    )

    return application


app = create_application()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "docs_url": "/docs",
        "api_version": settings.api_v1_prefix,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
    }
