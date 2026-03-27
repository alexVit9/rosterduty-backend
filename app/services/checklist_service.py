import uuid
from datetime import datetime, date, time, timezone
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.checklist_template import ChecklistTemplate, ChecklistItem
from app.models.completed_checklist import CompletedChecklist, CompletedChecklistItem
from app.models.user import User
from app.schemas.checklist_template import ChecklistTemplateCreate, ChecklistTemplateUpdate
from app.schemas.completed_checklist import CompleteChecklistRequest


async def get_templates_for_restaurant(
    restaurant_id: uuid.UUID,
    db: AsyncSession,
    location_id: Optional[uuid.UUID] = None,
    department_id: Optional[uuid.UUID] = None,
) -> list[ChecklistTemplate]:
    query = (
        select(ChecklistTemplate)
        .options(selectinload(ChecklistTemplate.items))
        .where(ChecklistTemplate.restaurant_id == restaurant_id)
    )
    if location_id:
        query = query.where(ChecklistTemplate.location_id == location_id)
    if department_id:
        query = query.where(ChecklistTemplate.department_id == department_id)
    query = query.order_by(ChecklistTemplate.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_template_by_id(
    template_id: uuid.UUID, restaurant_id: uuid.UUID, db: AsyncSession
) -> ChecklistTemplate:
    result = await db.execute(
        select(ChecklistTemplate)
        .options(selectinload(ChecklistTemplate.items))
        .where(
            ChecklistTemplate.id == template_id,
            ChecklistTemplate.restaurant_id == restaurant_id,
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist template not found",
        )

    return template


async def create_template(
    data: ChecklistTemplateCreate,
    manager_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    db: AsyncSession,
) -> ChecklistTemplate:
    template = ChecklistTemplate(
        id=uuid.uuid4(),
        name=data.name,
        description=data.description,
        location_id=data.location_id,
        department_id=data.department_id,
        time_from=data.time_from,
        time_to=data.time_to,
        recurrence_type=data.recurrence_type,
        recurrence_day_of_week=data.recurrence_day_of_week,
        recurrence_day_of_month=data.recurrence_day_of_month,
        created_by=manager_id,
        restaurant_id=restaurant_id,
    )
    db.add(template)
    await db.flush()

    for item_data in data.items:
        item = ChecklistItem(
            id=uuid.uuid4(),
            template_id=template.id,
            name=item_data.name,
            description=item_data.description,
            requires_photo=item_data.requires_photo,
            order=item_data.order,
            example_photo_urls=item_data.example_photo_urls,
        )
        db.add(item)

    await db.commit()
    await db.refresh(template)

    result = await db.execute(
        select(ChecklistTemplate)
        .options(selectinload(ChecklistTemplate.items))
        .where(ChecklistTemplate.id == template.id)
    )
    return result.scalar_one()


async def update_template(
    template_id: uuid.UUID,
    data: ChecklistTemplateUpdate,
    restaurant_id: uuid.UUID,
    db: AsyncSession,
) -> ChecklistTemplate:
    template = await get_template_by_id(template_id, restaurant_id, db)

    if data.name is not None:
        template.name = data.name
    if data.description is not None:
        template.description = data.description
    if data.location_id is not None:
        template.location_id = data.location_id
    if data.department_id is not None:
        template.department_id = data.department_id
    if data.time_from is not None:
        template.time_from = data.time_from
    if data.time_to is not None:
        template.time_to = data.time_to
    # recurrence fields support explicit None to clear them
    if 'recurrence_type' in data.model_fields_set:
        template.recurrence_type = data.recurrence_type
    if 'recurrence_day_of_week' in data.model_fields_set:
        template.recurrence_day_of_week = data.recurrence_day_of_week
    if 'recurrence_day_of_month' in data.model_fields_set:
        template.recurrence_day_of_month = data.recurrence_day_of_month

    if data.items is not None:
        # Delete existing items
        for item in template.items:
            await db.delete(item)
        await db.flush()

        # Create new items
        for item_data in data.items:
            item = ChecklistItem(
                id=uuid.uuid4(),
                template_id=template.id,
                name=item_data.name,
                description=item_data.description,
                requires_photo=item_data.requires_photo,
                order=item_data.order,
                example_photo_urls=item_data.example_photo_urls,
            )
            db.add(item)

    await db.commit()

    result = await db.execute(
        select(ChecklistTemplate)
        .options(selectinload(ChecklistTemplate.items))
        .where(ChecklistTemplate.id == template.id)
    )
    return result.scalar_one()


async def delete_template(
    template_id: uuid.UUID, restaurant_id: uuid.UUID, db: AsyncSession
) -> None:
    template = await get_template_by_id(template_id, restaurant_id, db)

    # Delete completed checklists referencing this template (FK is RESTRICT)
    completed_result = await db.execute(
        select(CompletedChecklist)
        .options(selectinload(CompletedChecklist.items))
        .where(CompletedChecklist.template_id == template_id)
    )
    for completed in completed_result.scalars().all():
        await db.delete(completed)
    await db.flush()

    await db.delete(template)
    await db.commit()


def _matches_recurrence(t: ChecklistTemplate, today: date) -> bool:
    """Return True if template should appear today based on recurrence settings."""
    if t.recurrence_type is None or t.recurrence_type == "daily":
        return True
    if t.recurrence_type == "weekly":
        # today.weekday(): 0=Mon, 6=Sun
        return t.recurrence_day_of_week is not None and today.weekday() == t.recurrence_day_of_week
    if t.recurrence_type == "monthly":
        return t.recurrence_day_of_month is not None and today.day == t.recurrence_day_of_month
    return True


async def get_active_templates_for_employee(
    restaurant_id: uuid.UUID,
    employee_id: uuid.UUID,
    db: AsyncSession,
) -> list[dict]:
    now = datetime.now(timezone.utc).time().replace(tzinfo=None)
    today = datetime.now(timezone.utc).date()

    result = await db.execute(
        select(ChecklistTemplate)
        .options(selectinload(ChecklistTemplate.items))
        .where(ChecklistTemplate.restaurant_id == restaurant_id)
    )
    all_templates = list(result.scalars().all())

    # Show all templates for today based on recurrence only.
    # Time window is informational — the client shows the timer and locks the form.
    templates = [
        t for t in all_templates
        if _matches_recurrence(t, today)
    ]

    # Check which ones this employee has already completed today
    completed_result = await db.execute(
        select(CompletedChecklist.template_id).where(
            CompletedChecklist.restaurant_id == restaurant_id,
            CompletedChecklist.completed_by == employee_id,
            CompletedChecklist.date == today,
        )
    )
    completed_template_ids = set(completed_result.scalars().all())

    # Load location and department names
    from app.models.restaurant import Location
    from app.models.department import Department

    loc_ids = {t.location_id for t in templates if t.location_id}
    dept_ids = {t.department_id for t in templates if t.department_id}

    locations_map: dict[uuid.UUID, str] = {}
    if loc_ids:
        loc_result = await db.execute(select(Location).where(Location.id.in_(loc_ids)))
        for loc in loc_result.scalars().all():
            locations_map[loc.id] = loc.name

    departments_map: dict[uuid.UUID, str] = {}
    if dept_ids:
        dept_result = await db.execute(select(Department).where(Department.id.in_(dept_ids)))
        for dept in dept_result.scalars().all():
            departments_map[dept.id] = dept.name

    return [
        {
            "template": t,
            "is_completed": t.id in completed_template_ids,
            "location_name": locations_map.get(t.location_id) if t.location_id else None,
            "department_name": departments_map.get(t.department_id) if t.department_id else None,
        }
        for t in templates
    ]


async def complete_checklist(
    data: CompleteChecklistRequest,
    employee: User,
    db: AsyncSession,
) -> CompletedChecklist:
    # Load template
    result = await db.execute(
        select(ChecklistTemplate)
        .options(selectinload(ChecklistTemplate.items))
        .where(
            ChecklistTemplate.id == data.template_id,
            ChecklistTemplate.restaurant_id == employee.restaurant_id,
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist template not found",
        )

    # Validate items
    template_items_map = {item.id: item for item in template.items}
    submitted_ids = {item.checklist_item_id for item in data.items}

    if submitted_ids != set(template_items_map.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submitted items do not match template items",
        )

    # Validate photo requirement — only if item is marked as completed
    for submitted_item in data.items:
        template_item = template_items_map[submitted_item.checklist_item_id]
        if template_item.requires_photo and submitted_item.completed and not submitted_item.photo_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item '{template_item.name}' requires a photo",
            )

    today = data.client_date or datetime.now(timezone.utc).date()

    completed = CompletedChecklist(
        id=uuid.uuid4(),
        template_id=template.id,
        template_name=template.name,
        date=today,
        completed_by=employee.id,
        restaurant_id=employee.restaurant_id,
        location_id=template.location_id,
        department_id=template.department_id,
    )
    db.add(completed)
    await db.flush()

    for submitted_item in data.items:
        template_item = template_items_map[submitted_item.checklist_item_id]
        if template_item.requires_photo:
            is_completed = bool(submitted_item.photo_url)
        else:
            is_completed = submitted_item.completed
        completed_item = CompletedChecklistItem(
            id=uuid.uuid4(),
            completed_checklist_id=completed.id,
            checklist_item_id=submitted_item.checklist_item_id,
            name=template_item.name,
            requires_photo=template_item.requires_photo,
            completed=is_completed,
            photo_url=submitted_item.photo_url,
            comment=submitted_item.comment,
        )
        db.add(completed_item)

    await db.commit()

    result = await db.execute(
        select(CompletedChecklist)
        .options(selectinload(CompletedChecklist.items))
        .where(CompletedChecklist.id == completed.id)
    )
    return result.scalar_one()


async def get_history(
    restaurant_id: uuid.UUID,
    filter_date: date,
    db: AsyncSession,
    location_id: Optional[uuid.UUID] = None,
) -> list[CompletedChecklist]:
    query = (
        select(CompletedChecklist)
        .options(
            selectinload(CompletedChecklist.completed_by_user),
            selectinload(CompletedChecklist.items),
        )
        .where(
            CompletedChecklist.restaurant_id == restaurant_id,
            CompletedChecklist.date == filter_date,
        )
    )
    if location_id:
        query = query.where(CompletedChecklist.location_id == location_id)
    query = query.order_by(CompletedChecklist.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_completed_checklist_detail(
    completed_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    db: AsyncSession,
) -> CompletedChecklist:
    result = await db.execute(
        select(CompletedChecklist)
        .options(
            selectinload(CompletedChecklist.items),
            selectinload(CompletedChecklist.completed_by_user),
        )
        .where(
            CompletedChecklist.id == completed_id,
            CompletedChecklist.restaurant_id == restaurant_id,
        )
    )
    completed = result.scalar_one_or_none()

    if not completed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completed checklist not found",
        )

    return completed


async def get_my_history(
    employee_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    db: AsyncSession,
) -> list[CompletedChecklist]:
    result = await db.execute(
        select(CompletedChecklist)
        .options(selectinload(CompletedChecklist.items))
        .where(
            CompletedChecklist.completed_by == employee_id,
            CompletedChecklist.restaurant_id == restaurant_id,
        )
        .order_by(CompletedChecklist.date.desc(), CompletedChecklist.created_at.desc())
    )
    return list(result.scalars().all())


async def get_dashboard_today(
    restaurant_id: uuid.UUID, db: AsyncSession
) -> list[dict]:
    now = datetime.now(timezone.utc).time().replace(tzinfo=None)
    today = datetime.now(timezone.utc).date()

    result = await db.execute(
        select(ChecklistTemplate)
        .options(selectinload(ChecklistTemplate.items))
        .where(ChecklistTemplate.restaurant_id == restaurant_id)
    )
    all_templates = list(result.scalars().all())

    # Filter by recurrence only (time window is informational on the manager dashboard)
    templates = [
        t for t in all_templates
        if _matches_recurrence(t, today)
    ]

    completed_result = await db.execute(
        select(CompletedChecklist)
        .options(
            selectinload(CompletedChecklist.completed_by_user),
            selectinload(CompletedChecklist.items),
        )
        .where(
            CompletedChecklist.restaurant_id == restaurant_id,
            CompletedChecklist.date == today,
        )
    )
    completed_list = list(completed_result.scalars().all())

    completed_map: dict[uuid.UUID, CompletedChecklist] = {}
    for c in completed_list:
        if c.template_id not in completed_map:
            completed_map[c.template_id] = c

    # Load ALL locations for the restaurant
    from app.models.restaurant import Location
    all_locs_result = await db.execute(
        select(Location).where(Location.restaurant_id == restaurant_id)
    )
    all_locations = list(all_locs_result.scalars().all())
    locations_map: dict[uuid.UUID, str] = {loc.id: loc.name for loc in all_locations}

    # Load departments for name resolution
    department_ids = {t.department_id for t in templates if t.department_id}
    departments_map: dict[uuid.UUID, str] = {}
    if department_ids:
        from app.models.department import Department
        dept_result = await db.execute(
            select(Department).where(Department.id.in_(department_ids))
        )
        for dept in dept_result.scalars().all():
            departments_map[dept.id] = dept.name

    # Group templates by location
    no_location_key = "Без локации"
    groups: dict[str, list[dict]] = {}
    # Pre-populate all known location groups
    for loc in all_locations:
        groups[loc.name] = []

    global_entries: list[dict] = []  # templates with no location_id → appear in all groups

    for t in templates:
        total_items = len(t.items)
        completed_obj = completed_map.get(t.id)
        completed_items = sum(1 for i in completed_obj.items if i.completed) if completed_obj else 0

        entry = {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "location_id": t.location_id,
            "department_id": t.department_id,
            "department_name": departments_map.get(t.department_id) if t.department_id else None,
            "time_from": t.time_from.strftime("%H:%M") if t.time_from else None,
            "time_to": t.time_to.strftime("%H:%M") if t.time_to else None,
            "recurrence_type": t.recurrence_type,
            "recurrence_day_of_week": t.recurrence_day_of_week,
            "recurrence_day_of_month": t.recurrence_day_of_month,
            "is_completed": t.id in completed_map,
            "completed_by_name": completed_obj.completed_by_user.name if completed_obj else None,
            "total_items": total_items,
            "completed_items": completed_items,
        }

        if t.location_id:
            loc_name = locations_map.get(t.location_id, no_location_key)
            groups.setdefault(loc_name, []).append(entry)
        else:
            global_entries.append(entry)

    # "All locations" templates appear in every location group
    if all_locations:
        for loc in all_locations:
            groups[loc.name].extend(global_entries)
    else:
        # No locations defined — show all under a single group
        groups.setdefault(no_location_key, []).extend(global_entries)

    # Only return groups that have at least one template
    return [
        {"location_name": loc_name, "templates": tmpls}
        for loc_name, tmpls in groups.items()
        if tmpls
    ]
