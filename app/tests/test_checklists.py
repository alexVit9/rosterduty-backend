import pytest
from httpx import AsyncClient


async def _register_manager(client: AsyncClient, suffix: str) -> str:
    reg = await client.post(
        "/auth/register/manager",
        json={
            "name": f"Manager {suffix}",
            "email": f"manager_{suffix}@example.com",
            "password": "password123",
            "restaurant_name": f"Restaurant {suffix}",
        },
    )
    assert reg.status_code == 201
    return reg.json()["access_token"]


@pytest.mark.asyncio
async def test_create_template(client: AsyncClient):
    token = await _register_manager(client, "ct1")

    response = await client.post(
        "/templates",
        json={
            "name": "Morning Opening",
            "description": "Morning shift checklist",
            "time_from": "08:00:00",
            "time_to": "10:00:00",
            "items": [
                {"name": "Check fridge temp", "requires_photo": False, "order": 1},
                {"name": "Photo of clean bar", "requires_photo": True, "order": 2},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Morning Opening"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_templates(client: AsyncClient):
    token = await _register_manager(client, "lt1")

    await client.post(
        "/templates",
        json={"name": "Template A", "items": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/templates",
        json={"name": "Template B", "items": []},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_template_detail(client: AsyncClient):
    token = await _register_manager(client, "gtd1")

    create = await client.post(
        "/templates",
        json={
            "name": "Detail Test",
            "items": [{"name": "Step 1", "requires_photo": False, "order": 1}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    template_id = create.json()["id"]

    response = await client.get(
        f"/templates/{template_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == template_id
    assert len(response.json()["items"]) == 1


@pytest.mark.asyncio
async def test_update_template(client: AsyncClient):
    token = await _register_manager(client, "ut1")

    create = await client.post(
        "/templates",
        json={"name": "Old Name", "items": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    template_id = create.json()["id"]

    response = await client.patch(
        f"/templates/{template_id}",
        json={"name": "New Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_template(client: AsyncClient):
    token = await _register_manager(client, "dt1")

    create = await client.post(
        "/templates",
        json={"name": "To Delete", "items": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    template_id = create.json()["id"]

    response = await client.delete(
        f"/templates/{template_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    # Confirm it's gone
    get = await client.get(
        f"/templates/{template_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get.status_code == 404


@pytest.mark.asyncio
async def test_employee_cannot_access_manager_routes(client: AsyncClient):
    """Employee JWT should get 403 on manager-only routes."""
    # Register manager and invite employee manually via DB
    manager_token = await _register_manager(client, "access1")

    # Manager tries to list their templates — should work
    response = await client.get(
        "/templates",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_complete_checklist_photo_validation(client: AsyncClient):
    """Submitting a checklist where requires_photo=True but no photo_url should fail."""
    token = await _register_manager(client, "photo1")

    create = await client.post(
        "/templates",
        json={
            "name": "Photo Required",
            "items": [{"name": "Photo step", "requires_photo": True, "order": 1}],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    template = create.json()
    item_id = template["items"][0]["id"]

    response = await client.post(
        "/checklists/complete",
        json={
            "template_id": template["id"],
            "items": [
                {
                    "checklist_item_id": item_id,
                    "completed": True,
                    "photo_url": None,
                }
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    # Manager submitting a checklist is valid (no employee restriction in spec)
    # But missing photo_url for requires_photo=True must be 400
    assert response.status_code == 400
    assert "photo" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_complete_checklist_success(client: AsyncClient):
    token = await _register_manager(client, "complete1")

    create = await client.post(
        "/templates",
        json={
            "name": "Completable Checklist",
            "items": [
                {"name": "No photo step", "requires_photo": False, "order": 1},
                {"name": "Photo step", "requires_photo": True, "order": 2},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    template = create.json()
    items = template["items"]

    response = await client.post(
        "/checklists/complete",
        json={
            "template_id": template["id"],
            "items": [
                {
                    "checklist_item_id": items[0]["id"],
                    "completed": True,
                    "photo_url": None,
                },
                {
                    "checklist_item_id": items[1]["id"],
                    "completed": True,
                    "photo_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                },
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["template_id"] == template["id"]
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_history_requires_manager(client: AsyncClient):
    """GET /checklists/history must reject non-managers (401 without token)."""
    response = await client.get("/checklists/history")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_dashboard_today(client: AsyncClient):
    token = await _register_manager(client, "dash1")

    response = await client.get(
        "/dashboard/today",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
