from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    quantity: int
    category_id: int
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)