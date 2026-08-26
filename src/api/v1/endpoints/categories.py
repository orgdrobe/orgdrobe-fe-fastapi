from fastapi import APIRouter

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from schemas.category_master import NewMasterCategory, MasterCategoryOut, UpdateMasterCategory
from services.interfaces import CategoryMasterServiceInterface
from schemas.errors import ErrorResponse
from dependencies import get_category_master_service, get_current_user, require_role
from models import User

router = APIRouter()

@router.get(
    "/master/", 
    response_model=list[MasterCategoryOut],
    status_code=status.HTTP_200_OK
)
async def master_categories_all(
    category_service: Annotated[CategoryMasterServiceInterface, Depends(get_category_master_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100
) -> list[MasterCategoryOut]:
    return await category_service.get_all(skip=skip, limit=limit)


@router.get(
    "/master/{id}", 
    response_model=MasterCategoryOut,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Category not found"},
    }
)
async def master_category_by_id(
    id: int, 
    category_service: Annotated[CategoryMasterServiceInterface, Depends(get_category_master_service)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> MasterCategoryOut:
    result = await category_service.get_by_id(id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return result


@router.post(
    "/master/",
    response_model=MasterCategoryOut,
    status_code=status.HTTP_201_CREATED
)
async def create_master_category(
    payload: NewMasterCategory,
    category_service: Annotated[CategoryMasterServiceInterface, Depends(get_category_master_service)],
    current_user: Annotated[User, Depends(require_role(["admin"]))]
) -> MasterCategoryOut:
    return await category_service.create(payload)


@router.patch(
    "/master/{id}",
    response_model=MasterCategoryOut,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Category not found"},
    }
)
async def update_master_category(
    id: int,
    payload: UpdateMasterCategory,
    category_service: Annotated[CategoryMasterServiceInterface, Depends(get_category_master_service)],
    current_user: Annotated[User, Depends(require_role(["admin"]))]
) -> MasterCategoryOut:
    return await category_service.update(id, payload)


@router.delete(
    "/master/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Category not found"},
    }
)
async def delete_master_category(
    id: int,
    category_service: Annotated[CategoryMasterServiceInterface, Depends(get_category_master_service)],
    current_user: Annotated[User, Depends(require_role(["admin"]))]
) -> None:
    await category_service.delete(id)


# ---------------------------------------------------------
# SUB CATEGORIES
# ---------------------------------------------------------

@router.get("/sub/", response_model=list[dict])
async def sub_categories_all(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return []

@router.get("/sub/{id}", response_model=dict)
async def sub_category_by_id(
    id: int, 
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {}
