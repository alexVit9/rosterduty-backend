import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import require_manager
from app.services.checklist_service import (
    get_templates_for_restaurant,
    get_template_by_id,
    create_template,
    update_template,
    delete_template,
)
from app.schemas.checklist_template import (
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
    ChecklistTemplateResponse,
)
from app.models.user import User

router = APIRouter(prefix="/templates", tags=["checklist-templates"])


@router.get("", response_model=list[ChecklistTemplateResponse])
async def list_templates(
    location_id: Optional[uuid.UUID] = Query(default=None),
    department_id: Optional[uuid.UUID] = Query(default=None),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    templates = await get_templates_for_restaurant(
        current_user.restaurant_id, db, location_id, department_id
    )
    return [ChecklistTemplateResponse.model_validate(t) for t in templates]


@router.post("", response_model=ChecklistTemplateResponse, status_code=201)
async def create_template_endpoint(
    data: ChecklistTemplateCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    template = await create_template(data, current_user.id, current_user.restaurant_id, db)
    return ChecklistTemplateResponse.model_validate(template)


@router.get("/{template_id}", response_model=ChecklistTemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    template = await get_template_by_id(template_id, current_user.restaurant_id, db)
    return ChecklistTemplateResponse.model_validate(template)


@router.patch("/{template_id}", response_model=ChecklistTemplateResponse)
async def update_template_endpoint(
    template_id: uuid.UUID,
    data: ChecklistTemplateUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    template = await update_template(template_id, data, current_user.restaurant_id, db)
    return ChecklistTemplateResponse.model_validate(template)


@router.delete("/{template_id}", status_code=204)
async def delete_template_endpoint(
    template_id: uuid.UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    await delete_template(template_id, current_user.restaurant_id, db)
