from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.services.dashboard import calculate_dashboard_stats


def test_dashboard_service_only_counts_the_requested_owner(db_session: Session) -> None:
    owner = User(email="owner@example.com", password_hash="not-used-in-this-unit-test")
    other_user = User(email="other@example.com", password_hash="not-used-in-this-unit-test")
    db_session.add_all([owner, other_user])
    db_session.flush()
    project = Project(name="Owner project", owner_id=owner.id)
    other_project = Project(name="Other project", owner_id=other_user.id)
    db_session.add_all([project, other_project])
    db_session.flush()
    db_session.add_all(
        [
            Task(
                title="Overdue owner task",
                project_id=project.id,
                priority=TaskPriority.HIGH,
                due_date=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1),
            ),
            Task(title="Other user task", project_id=other_project.id),
        ]
    )
    db_session.commit()

    stats = calculate_dashboard_stats(db_session, owner.id)

    assert stats.total_tasks == 1
    assert stats.overdue_tasks == 1
    assert stats.by_priority[TaskPriority.HIGH] == 1
    assert stats.by_status[TaskStatus.TODO] == 1
