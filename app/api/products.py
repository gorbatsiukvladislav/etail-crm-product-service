from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.product import ProductCreate, Product, CategoryCreate, Category
from app.services.product import ProductService
from app.utils.redis_cache import cache
from app.utils.rabbitmq import publish_event

router = APIRouter()

@router.post("/categories/", response_model=Category)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    db_category = await service.create_category(category)
    await publish_event("category.created", db_category.dict())
    return db_category

@router.get("/categories/", response_model=List[Category])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    cache_key = f"categories:skip={skip}:limit={limit}"
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result

    service = ProductService(db)
    categories = await service.get_categories(skip=skip, limit=limit)
    
    await cache.set(cache_key, categories)
    return categories

@router.post("/products/", response_model=Product)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    db_product = await service.create_product(product)
    await publish_event("product.created", db_product.dict())
    return db_product

@router.get("/products/", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    cache_key = f"products:skip={skip}:limit={limit}"
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result

    service = ProductService(db)
    products = await service.get_products(skip=skip, limit=limit)
    
    await cache.set(cache_key, products)
    return products

@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    cache_key = f"product:{product_id}"
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result

    service = ProductService(db)
    product = await service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await cache.set(cache_key, product)
    return product