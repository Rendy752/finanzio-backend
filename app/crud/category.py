from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, func, or_
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.category import Category
from app.schemas.category import CategoryCreate

# --- Read Operations ---

async def get_category_by_id(db: AsyncSession, category_id: UUID, user_id: UUID) -> Optional[Category]:
    """Retrieves a single category by ID, ensuring it belongs to the user or is a system default."""
    result = await db.execute(
        select(Category)
        .where(Category.category_id == category_id)
        .where(or_(Category.user_id == user_id, Category.user_id.is_(None)))
    )
    return result.scalars().first()

async def get_all_categories_for_user(
    db: AsyncSession, 
    user_id: UUID, 
    q: Optional[str] = None, 
    limit: int = 10, 
    offset: int = 0
) -> Tuple[List[Category], int]:
    """Retrieves all categories for a specific user (including system defaults), with search and pagination."""
    
    base_query = select(Category).where(
        or_(Category.user_id == user_id, Category.user_id.is_(None))
    )
    
    # 1. Apply Search Filter
    if q:
        search_term = f"%{q}%"
        base_query = base_query.where(Category.category_name.ilike(search_term))
        
    # 2. Get Total Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    # 3. Apply Ordering and Pagination
    final_query = base_query.order_by(Category.category_name).limit(limit).offset(offset)
    
    result = await db.execute(final_query)
    categories = result.scalars().all()
    
    return categories, total_count

# --- Write Operations ---

async def create_category(db: AsyncSession, category_in: CategoryCreate, user_id: UUID) -> Category:
    """Creates a new user-defined category."""
    db_category = Category(
        user_id=user_id,
        category_name=category_in.category_name,
        type=category_in.type # Enum type
    )
    
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    
    return db_category

async def update_category(db: AsyncSession, category_id: UUID, user_id: UUID, category_in: CategoryCreate) -> Optional[Category]:
    """Updates a user-owned category, preventing updates to system defaults (user_id is NOT NULL)."""
    
    existing_category = await get_category_by_id(db, category_id, user_id)

    # Check if category exists AND belongs to the user (not a system default)
    if not existing_category or existing_category.user_id is None:
        return None

    stmt = (
        update(Category)
        .where(Category.category_id == category_id)
        .where(Category.user_id == user_id)
        .values(
            category_name=category_in.category_name,
            type=category_in.type
        )
        .returning(Category)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.scalars().first()

async def delete_category(db: AsyncSession, category_id: UUID, user_id: UUID) -> bool:
    """Deletes a user-owned category, preventing deletion of system defaults."""
    
    existing_category = await get_category_by_id(db, category_id, user_id)
    if not existing_category or existing_category.user_id is None:
        return False
        
    stmt = (
        delete(Category)
        .where(Category.category_id == category_id)
        .where(Category.user_id == user_id) 
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0