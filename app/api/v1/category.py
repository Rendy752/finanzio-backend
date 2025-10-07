from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.core.db import get_db
from app.crud import category as crud_category
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.common import APIResponse, APIListResponse
from app.api.v1.dependencies import CurrentUser 

router = APIRouter(prefix="/categories", tags=["Categories"])

DB_SESSION = Depends(get_db)

@router.post(
    "/",
    response_model=APIResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction category."
)
async def create_category(
    category_in: CategoryCreate,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Creates a new user-defined category (e.g., Food, Salary)."""
    db_category = await crud_category.create_category(
        db, 
        category_in=category_in, 
        user_id=current_user.user_id
    )
    
    return APIResponse(
        message="Category created successfully.",
        data=CategoryResponse.model_validate(db_category)
    )

@router.get(
    "/",
    response_model=APIListResponse[CategoryResponse],
    summary="Get all categories (including system defaults) for the authenticated user."
)
async def read_categories(
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION,
    q: Optional[str] = Query(None, description="Search by category name."),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieves a list of all user-owned and system default categories with search and pagination."""
    
    db_categories, total_count = await crud_category.get_all_categories_for_user(
        db, 
        user_id=current_user.user_id,
        q=q,
        limit=limit,
        offset=offset
    )
    
    return APIListResponse(
        message="Categories retrieved successfully.",
        data=[CategoryResponse.model_validate(c) for c in db_categories],
        total_count=total_count
    )
    
@router.get(
    "/{category_id}",
    response_model=APIResponse[CategoryResponse],
    summary="Get a specific category by ID."
)
async def read_category(
    category_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Retrieves details for a specific category, ensuring access rights (user-owned or system)."""
    
    db_category = await crud_category.get_category_by_id(
        db, 
        category_id=category_id, 
        user_id=current_user.user_id
    )
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or not accessible."
        )

    return APIResponse(
        message="Category retrieved successfully.",
        data=CategoryResponse.model_validate(db_category)
    )

@router.put(
    "/{category_id}",
    response_model=APIResponse[CategoryResponse],
    summary="Update category name and/or type."
)
async def update_category(
    category_id: uuid.UUID,
    category_in: CategoryCreate, 
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Updates a user-owned category (System categories cannot be updated)."""
    
    db_category = await crud_category.update_category(
        db,
        category_id=category_id,
        user_id=current_user.user_id,
        category_in=category_in
    )
    
    if not db_category:
        check_category = await crud_category.get_category_by_id(db, category_id, current_user.user_id)
        if check_category and check_category.user_id is None:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System categories cannot be updated."
            )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or not accessible for update."
        )
        
    return APIResponse(
        message="Category updated successfully.",
        data=CategoryResponse.model_validate(db_category)
    )

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response, 
    summary="Delete a specific user-owned category."
)
async def delete_category(
    category_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Deletes a user-owned category (System categories cannot be deleted)."""
    
    deleted = await crud_category.delete_category(
        db,
        category_id=category_id,
        user_id=current_user.user_id
    )

    if not deleted:
        check_category = await crud_category.get_category_by_id(db, category_id, current_user.user_id)
        if check_category and check_category.user_id is None:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System categories cannot be deleted."
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or not accessible for deletion."
        )
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)