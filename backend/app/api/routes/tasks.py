from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.api.routes.projects import get_owned_project
from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import DashboardStats, TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(tags=["tasks"])


def get_owned_task(task_id: int, user_id: int, db: DbSession) -> Task:
    task = db.scalar(
        select(Task).join(Project).where(Task.id == task_id, Project.owner_id == user_id)
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
def list_project_tasks(
    project_id: int,
    current_user: CurrentUser,
    db: DbSession,
    status_filter: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = None,
) -> list[Task]:
    get_owned_project(project_id, current_user.id, db)
    query = select(Task).where(Task.project_id == project_id)
    if status_filter is not None:
        query = query.where(Task.status == status_filter)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if search:
        query = query.where(Task.title.ilike(f"%{search.strip()}%"))
    return list(db.scalars(query.order_by(Task.id.desc())))


@router.post(
    "/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED
)
def create_task(
    project_id: int, payload: TaskCreate, current_user: CurrentUser, db: DbSession
) -> Task:
    get_owned_project(project_id, current_user.id, db)
    task = Task(**payload.model_dump(), project_id=project_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, current_user: CurrentUser, db: DbSession) -> Task:
    return get_owned_task(task_id, current_user.id, db)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, payload: TaskUpdate, current_user: CurrentUser, db: DbSession
) -> Task:
    task = get_owned_task(task_id, current_user.id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: CurrentUser, db: DbSession) -> Response:
    task = get_owned_task(task_id, current_user.id, db)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(current_user: CurrentUser, db: DbSession) -> DashboardStats:
    owner_tasks = select(Task).join(Project).where(Project.owner_id == current_user.id).subquery()
    status_counts = dict(
        db.execute(select(owner_tasks.c.status, func.count()).group_by(owner_tasks.c.status))
    )
    priority_counts = dict(
        db.execute(select(owner_tasks.c.priority, func.count()).group_by(owner_tasks.c.priority))
    )
    total_tasks = db.scalar(select(func.count()).select_from(owner_tasks)) or 0
    overdue_tasks = (
        db.scalar(
            select(func.count())
            .select_from(owner_tasks)
            # MySQL DATETIME is timezone-naive; normalize UTC before comparing.
            .where(
                owner_tasks.c.due_date < datetime.now(UTC).replace(tzinfo=None),
                owner_tasks.c.status != TaskStatus.DONE,
            )
        )
        or 0
    )
    return DashboardStats(
        total_tasks=total_tasks,
        overdue_tasks=overdue_tasks,
        by_status={item: status_counts.get(item, 0) for item in TaskStatus},
        by_priority={item: priority_counts.get(item, 0) for item in TaskPriority},
    )
