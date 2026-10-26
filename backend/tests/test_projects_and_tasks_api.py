from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def create_project(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Assessment project", "description": "TaskFlow API tests"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_project_crud_and_task_search_filters(
    client: TestClient, user_headers: dict[str, str]
) -> None:
    project_id = create_project(client, user_headers)
    listed = client.get("/api/v1/projects", headers=user_headers)
    updated = client.patch(
        f"/api/v1/projects/{project_id}", headers=user_headers, json={"name": "Updated project"}
    )
    task = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=user_headers,
        json={"title": "Write tests", "status": "in_progress", "priority": "high"},
    )
    filtered = client.get(
        f"/api/v1/projects/{project_id}/tasks?status_filter=in_progress&search=tests",
        headers=user_headers,
    )

    assert listed.status_code == 200
    assert listed.json()[0]["id"] == project_id
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated project"
    assert task.status_code == 201
    assert filtered.status_code == 200
    assert [item["title"] for item in filtered.json()] == ["Write tests"]

    deleted_task = client.delete(f"/api/v1/tasks/{task.json()['id']}", headers=user_headers)
    deleted_project = client.delete(f"/api/v1/projects/{project_id}", headers=user_headers)
    assert deleted_task.status_code == 204
    assert deleted_project.status_code == 204


def test_dashboard_reports_counts_and_overdue_tasks(
    client: TestClient, user_headers: dict[str, str]
) -> None:
    project_id = create_project(client, user_headers)
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    for payload in (
        {"title": "Late work", "priority": "high", "due_date": past},
        {"title": "Completed work", "status": "done", "priority": "low", "due_date": past},
        {"title": "Future work", "status": "in_progress", "due_date": future},
    ):
        response = client.post(
            f"/api/v1/projects/{project_id}/tasks", headers=user_headers, json=payload
        )
        assert response.status_code == 201, response.text

    stats = client.get("/api/v1/dashboard/stats", headers=user_headers)

    assert stats.status_code == 200
    assert stats.json() == {
        "total_tasks": 3,
        "overdue_tasks": 1,
        "by_status": {"todo": 1, "in_progress": 1, "done": 1},
        "by_priority": {"low": 1, "medium": 1, "high": 1},
    }


def test_user_cannot_access_another_users_project_or_task(
    client: TestClient, user_headers: dict[str, str], second_user_headers: dict[str, str]
) -> None:
    project_id = create_project(client, user_headers)
    task = client.post(
        f"/api/v1/projects/{project_id}/tasks", headers=user_headers, json={"title": "Private task"}
    )
    task_id = task.json()["id"]

    responses = [
        client.get(f"/api/v1/projects/{project_id}", headers=second_user_headers),
        client.patch(
            f"/api/v1/projects/{project_id}", headers=second_user_headers, json={"name": "No"}
        ),
        client.delete(f"/api/v1/projects/{project_id}", headers=second_user_headers),
        client.get(f"/api/v1/tasks/{task_id}", headers=second_user_headers),
        client.patch(f"/api/v1/tasks/{task_id}", headers=second_user_headers, json={"title": "No"}),
        client.delete(f"/api/v1/tasks/{task_id}", headers=second_user_headers),
    ]

    assert all(response.status_code == 404 for response in responses)


def test_invalid_input_returns_422_and_health_uses_test_database(client: TestClient) -> None:
    invalid_email = client.post(
        "/api/v1/auth/register", json={"email": "not-an-email", "password": "short"}
    )
    health = client.get("/health")

    assert invalid_email.status_code == 422
    assert invalid_email.json()["error"]["code"] == "validation_error"
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "database": "connected"}
