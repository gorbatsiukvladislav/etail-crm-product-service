from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import products
from config.settings import settings

from app.utils.redis_cache import cache
from app.utils.rabbitmq import rabbitmq
from app.core.events import setup_event_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    await cache.init()
    await rabbitmq.connect()
    await setup_event_handlers()

@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    await cache.close()
    await rabbitmq.close()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    products.router,
    prefix=f"{settings.API_V1_STR}/products",
    tags=["products"]
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}