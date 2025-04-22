from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.events import (
    init_redis,
    close_redis,
    init_rabbitmq,
    close_rabbitmq
)
from app.api import products

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application"""
    # Startup
    await init_redis()
    await init_rabbitmq()
    
    yield
    
    # Shutdown
    await close_redis()
    await close_rabbitmq()

def create_application() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Product Service",
        description="Product Service API",
        version="1.0.0",
        lifespan=lifespan
    )

    # Include routers
    app.include_router(
        products.router,
        prefix="/api/v1/products",
        tags=["products"]
    )

    return app

app = create_application()