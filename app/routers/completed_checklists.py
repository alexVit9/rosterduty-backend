import uuid
from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import get_current_user, require_manager
from app.services.checklist_service import (
    get_active_templates_for_employee,
    complete_checklist,
    get_history,
    get_completed_checklist_detail,
    get_my_history,
    get_dashboard_today,
)
from app.schemas.checklist_template import ActiveTemplateResponse, ChecklistItemResponse
from app.schemas.completed_checklist import (
    CompleteChecklistRequest,
    CompletedChecklistResponse,
    CompletedChecklistSummary,
    CompletedChecklistItemResponse,
    DashboardLocationGroup,
)
from app.models.user import User

router = APIRouter(tags=["checklists"])


@router.get("/checklists/active/today", response_model=list[ActiveTemplateResponse])
async def get_active_today(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    active = await get_active_templates_for_employee(
        current_user.restaurant_id, current_user.id, db
    )
    result = []
    for entry in active:
        t = entry["template"]
        result.append(
            ActiveTemplateResponse(
                id=t.id,
                name=t.name,
                description=t.description,
                location_id=t.location_id,
                location_name=entry["location_name"],
                department_id=t.department_id,
                department_name=entry["department_name"],
                time_from=t.time_from,
                time_to=t.time_to,
                recurrence_type=t.recurrence_type,
                recurrence_day_of_week=t.recurrence_day_of_week,
                recurrence_day_of_month=t.recurrence_day_of_month,
                restaurant_id=t.restaurant_id,
                items=[ChecklistItemResponse.model_validate(i) for i in t.items],
                is_completed=entry["is_completed"],
            )
        )
    return result


@router.post("/checklists/complete", response_model=CompletedChecklistResponse, status_code=201)
async def submit_checklist(
    data: CompleteChecklistRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    completed = await complete_checklist(data, current_user, db)
    return _build_completed_response(completed)


@router.get("/checklists/history/my", response_model=list[CompletedChecklistSummary])
async def get_my_checklist_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    history = await get_my_history(current_user.id, current_user.restaurant_id, db)
    return [_build_summary(c) for c in history]


@router.get("/checklists/history/month-summary")
async def get_month_summary(
    year: int = Query(...),
    month: int = Query(...),
    location_id: Optional[uuid.UUID] = Query(default=None),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, extract
    from app.models.completed_checklist import CompletedChecklist
    from sqlalchemy.orm import selectinload

    query = (
        select(CompletedChecklist)
        .options(selectinload(CompletedChecklist.items))
        .where(
            CompletedChecklist.restaurant_id == current_user.restaurant_id,
            extract("year", CompletedChecklist.date) == year,
            extract("month", CompletedChecklist.date) == month,
        )
    )
    if location_id:
        query = query.where(CompletedChecklist.location_id == location_id)
    result = await db.execute(query)
    rows = result.scalars().all()

    # Group by date
    from collections import defaultdict
    by_date: dict = defaultdict(lambda: {"total": 0, "all_done": 0})
    for c in rows:
        d = c.date.isoformat()
        total = len(c.items)
        done = sum(1 for i in c.items if i.completed)
        by_date[d]["total"] += 1
        if done == total:
            by_date[d]["all_done"] += 1

    return [
        {"date": d, "total": v["total"], "all_done": v["all_done"]}
        for d, v in by_date.items()
    ]


@router.get("/checklists/history", response_model=list[CompletedChecklistSummary])
async def get_checklist_history(
    filter_date: Optional[date] = Query(
        default=None, alias="date", description="Filter by date (YYYY-MM-DD)"
    ),
    location_id: Optional[uuid.UUID] = Query(default=None),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    query_date = filter_date or datetime.now(timezone.utc).date()
    history = await get_history(current_user.restaurant_id, query_date, db, location_id)
    return [_build_summary(c) for c in history]


@router.get("/checklists/history/{completed_id}", response_model=CompletedChecklistResponse)
async def get_completed_detail(
    completed_id: uuid.UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    completed = await get_completed_checklist_detail(
        completed_id, current_user.restaurant_id, db
    )
    return _build_completed_response(completed)


@router.get("/dashboard/today", response_model=list[DashboardLocationGroup])
async def dashboard_today(
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    return await get_dashboard_today(current_user.restaurant_id, db)


def _build_summary(c) -> CompletedChecklistSummary:
    total = len(c.items)
    done = sum(1 for i in c.items if i.completed)
    return CompletedChecklistSummary(
        id=c.id,
        template_id=c.template_id,
        template_name=c.template_name,
        date=c.date,
        completed_by=c.completed_by,
        completed_by_name=c.completed_by_user.name if c.completed_by_user else None,
        restaurant_id=c.restaurant_id,
        location_id=c.location_id,
        department_id=c.department_id,
        created_at=c.created_at,
        total_items=total,
        completed_items=done,
    )


def _build_completed_response(completed) -> CompletedChecklistResponse:
    items = [
        CompletedChecklistItemResponse(
            id=item.id,
            checklist_item_id=item.checklist_item_id,
            name=item.name,
            requires_photo=item.requires_photo,
            completed=item.completed,
            photo_url=item.photo_url,
            comment=item.comment,
        )
        for item in completed.items
    ]
    return CompletedChecklistResponse(
        id=completed.id,
        template_id=completed.template_id,
        template_name=completed.template_name,
        date=completed.date,
        completed_by=completed.completed_by,
        completed_by_name=(
            completed.completed_by_user.name if completed.completed_by_user else None
        ),
        restaurant_id=completed.restaurant_id,
        location_id=completed.location_id,
        department_id=completed.department_id,
        created_at=completed.created_at,
        total_items=len(items),
        completed_items=sum(1 for i in items if i.completed),
        items=items,
    )
