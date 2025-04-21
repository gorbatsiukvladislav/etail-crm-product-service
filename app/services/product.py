from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from app.models.product import Product, Category
from app.schemas.product import ProductCreate, CategoryCreate

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def create_category(self, category: CategoryCreate) -> Category:
        db_category = Category(
            name=category.name,
            description=category.description
        )
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def get_category(self, category_id: int) -> Optional[Category]:
        return await self.db.query(Category).filter(Category.id == category_id).first()

    async def get_categories(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Category]:
        return await self.db.query(Category).offset(skip).limit(limit).all()

    async def create_product(self, product: ProductCreate) -> Product:
        # Verify category exists
        category = await self.get_category(product.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        db_product = Product(
            name=product.name,
            description=product.description,
            sku=product.sku,
            price=product.price,
            quantity=product.quantity,
            category_id=product.category_id,
            is_active=product.is_active
        )
        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def get_product(self, product_id: int) -> Optional[Product]:
        return await self.db.query(Product).filter(Product.id == product_id).first()

    async def get_products(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Product]:
        return await self.db.query(Product).offset(skip).limit(limit).all()

    async def update_product(
        self, 
        product_id: int, 
        product_data: ProductCreate
    ) -> Product:
        db_product = await self.get_product(product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Verify category exists if it's being updated
        if product_data.category_id != db_product.category_id:
            category = await self.get_category(product_data.category_id)
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

        for key, value in product_data.dict().items():
            setattr(db_product, key, value)

        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def delete_product(self, product_id: int) -> bool:
        db_product = await self.get_product(product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        await self.db.delete(db_product)
        await self.db.commit()
        return True