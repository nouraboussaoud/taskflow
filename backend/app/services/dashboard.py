from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import DashboardStats


def calculate_dashboard_stats(db: Session, user_id: int) -> DashboardStats:
    """Return task aggregates for exactly one owner's projects."""
    owner_tasks = select(Task).join(Project).where(Project.owner_id == user_id).subquery()
    status_counts = dict(
        db.execute(select(owner_tasks.c.status, func.count()).group_by(owner_tasks.c.status)).all()
    )
    priority_counts = dict(
        db.execute(
            select(owner_tasks.c.priority, func.count()).group_by(owner_tasks.c.priority)
        ).all()
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
