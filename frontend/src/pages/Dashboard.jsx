import { useCallback, useEffect, useState } from "react";

import { api } from "../api";
import { useAuth } from "../auth";
import { ErrorMessage, Loading, PriorityBadge, StatusBadge } from "../components";

const emptyProject = { name: "", description: "" };
const emptyTask = { title: "", description: "", status: "todo", priority: "medium", due_date: "" };

function toDateInput(value) {
  if (!value) return "";
  const utcDate = new Date(`${value}Z`);
  const localDate = new Date(utcDate.getTime() - utcDate.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 16);
}

function formatDueDate(value) {
  return new Date(`${value}Z`).toLocaleString();
}

export function Dashboard() {
  const { token, signOut } = useAuth();
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({ search: "", status_filter: "", priority: "" });
  const [projectForm, setProjectForm] = useState(emptyProject);
  const [taskForm, setTaskForm] = useState(emptyTask);
  const [editingProject, setEditingProject] = useState(null);
  const [editingTask, setEditingTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [reloadTasks, setReloadTasks] = useState(0);
  const [error, setError] = useState("");

  const request = useCallback((path, options = {}) => api(path, { token, ...options }), [token]);

  const refreshDashboard = useCallback(async () => {
    const [projectData, statsData] = await Promise.all([request("/projects"), request("/dashboard/stats")]);
    setProjects(projectData);
    setStats(statsData);
    setSelectedProjectId((current) =>
      projectData.some((project) => String(project.id) === current)
        ? current
        : String(projectData[0]?.id || ""),
    );
  }, [request]);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        await refreshDashboard();
      } catch (requestError) {
        if (active) setError(requestError.message);
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => { active = false; };
  }, [refreshDashboard]);

  useEffect(() => {
    if (!selectedProjectId) {
      setTasks([]);
      setTasksLoading(false);
      return undefined;
    }
    const controller = new AbortController();
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => { if (value) params.set(key, value); });
    setTasksLoading(true);
    request(`/projects/${selectedProjectId}/tasks?${params}`, { signal: controller.signal })
      .then((data) => { setTasks(data); setTasksLoading(false); })
      .catch((requestError) => {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
          setTasksLoading(false);
        }
      });
    return () => controller.abort();
  }, [filters, request, selectedProjectId, reloadTasks]);

  async function refreshAll() {
    setError("");
    try {
      await refreshDashboard();
      // Incrementing reruns the task query with the currently selected filters.
      setReloadTasks((current) => current + 1);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function saveProject(event) {
    event.preventDefault();
    setError("");
    try {
      if (editingProject) {
        await request(`/projects/${editingProject.id}`, { method: "PATCH", body: projectForm });
      } else {
        const created = await request("/projects", { method: "POST", body: projectForm });
        setSelectedProjectId(String(created.id));
      }
      setProjectForm(emptyProject);
      setEditingProject(null);
      await refreshAll();
    } catch (requestError) { setError(requestError.message); }
  }

  async function deleteProject(projectId) {
    if (!window.confirm("Delete this project and all its tasks?")) return;
    try {
      await request(`/projects/${projectId}`, { method: "DELETE" });
      setSelectedProjectId("");
      await refreshAll();
    } catch (requestError) { setError(requestError.message); }
  }

  async function saveTask(event) {
    event.preventDefault();
    if (!selectedProjectId) return;
    const body = {
      ...taskForm,
      due_date: taskForm.due_date ? new Date(taskForm.due_date).toISOString() : null,
    };
    try {
      if (editingTask) await request(`/tasks/${editingTask.id}`, { method: "PATCH", body });
      else await request(`/projects/${selectedProjectId}/tasks`, { method: "POST", body });
      setTaskForm(emptyTask);
      setEditingTask(null);
      await refreshAll();
    } catch (requestError) { setError(requestError.message); }
  }

  async function deleteTask(taskId) {
    if (!window.confirm("Delete this task?")) return;
    try {
      await request(`/tasks/${taskId}`, { method: "DELETE" });
      await refreshAll();
    } catch (requestError) { setError(requestError.message); }
  }

  if (loading) return <main className="page"><Loading label="Loading your workspace…" /></main>;

  return (
    <main className="page">
      <header className="topbar">
        <div><p className="eyebrow">TaskFlow</p><h1>My workspace</h1></div>
        <button className="button-secondary" onClick={signOut}>Sign out</button>
      </header>
      <ErrorMessage message={error} />

      <section className="stats-grid" aria-label="Task statistics">
        <article><span>Total tasks</span><strong>{stats?.total_tasks ?? 0}</strong></article>
        <article><span>Overdue</span><strong className="danger-text">{stats?.overdue_tasks ?? 0}</strong></article>
        <article><span>In progress</span><strong>{stats?.by_status?.in_progress ?? 0}</strong></article>
        <article><span>High priority</span><strong>{stats?.by_priority?.high ?? 0}</strong></article>
      </section>

      <div className="workspace-grid">
        <aside className="panel projects-panel">
          <div className="panel-heading"><h2>Projects</h2></div>
          <form onSubmit={saveProject} className="stack-form compact-form">
            <label>Name<input value={projectForm.name} onChange={(event) => setProjectForm({ ...projectForm, name: event.target.value })} required /></label>
            <label>Description<textarea value={projectForm.description} onChange={(event) => setProjectForm({ ...projectForm, description: event.target.value })} /></label>
            <button type="submit">{editingProject ? "Save project" : "Add project"}</button>
            {editingProject && <button type="button" className="button-link" onClick={() => { setEditingProject(null); setProjectForm(emptyProject); }}>Cancel edit</button>}
          </form>
          <div className="project-list">
            {projects.length === 0 && <p className="muted">Create your first project.</p>}
            {projects.map((project) => (
              <div className={`project-item ${String(project.id) === selectedProjectId ? "selected" : ""}`} key={project.id}>
                <button className="project-select" onClick={() => setSelectedProjectId(String(project.id))}>{project.name}</button>
                <div><button className="icon-button" aria-label={`Edit ${project.name}`} onClick={() => { setEditingProject(project); setProjectForm({ name: project.name, description: project.description || "" }); }}>Edit</button><button className="icon-button danger" aria-label={`Delete ${project.name}`} onClick={() => deleteProject(project.id)}>Delete</button></div>
              </div>
            ))}
          </div>
        </aside>

        <section className="panel tasks-panel">
          <div className="panel-heading"><div><h2>Tasks</h2><p className="muted">Choose a project to manage its tasks.</p></div></div>
          {!selectedProjectId ? <p className="empty-state">Select or create a project to begin.</p> : <>
            <form onSubmit={saveTask} className="task-form">
              <input placeholder="Task title" value={taskForm.title} onChange={(event) => setTaskForm({ ...taskForm, title: event.target.value })} required />
              <select value={taskForm.status} onChange={(event) => setTaskForm({ ...taskForm, status: event.target.value })}><option value="todo">To do</option><option value="in_progress">In progress</option><option value="done">Done</option></select>
              <select value={taskForm.priority} onChange={(event) => setTaskForm({ ...taskForm, priority: event.target.value })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select>
              <input type="datetime-local" value={taskForm.due_date} onChange={(event) => setTaskForm({ ...taskForm, due_date: event.target.value })} />
              <textarea placeholder="Optional description" value={taskForm.description} onChange={(event) => setTaskForm({ ...taskForm, description: event.target.value })} />
              <button type="submit">{editingTask ? "Save task" : "Add task"}</button>
              {editingTask && <button type="button" className="button-link" onClick={() => { setEditingTask(null); setTaskForm(emptyTask); }}>Cancel edit</button>}
            </form>
            <div className="filters"><input placeholder="Search tasks" value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value })} /><select value={filters.status_filter} onChange={(event) => setFilters({ ...filters, status_filter: event.target.value })}><option value="">All statuses</option><option value="todo">To do</option><option value="in_progress">In progress</option><option value="done">Done</option></select><select value={filters.priority} onChange={(event) => setFilters({ ...filters, priority: event.target.value })}><option value="">All priorities</option><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></div>
            <div className="task-list">
              {tasksLoading ? <Loading label="Loading tasks..." /> : tasks.length === 0 ? (
                <p className="empty-state">No matching tasks.</p>
              ) : tasks.map((task) => (
                <article className="task-card" key={task.id}>
                  <div>
                    <h3>{task.title}</h3>
                    {task.description && <p>{task.description}</p>}
                    <div className="badges">
                      <StatusBadge status={task.status} />
                      <PriorityBadge priority={task.priority} />
                      {task.due_date && <span className="due-date">Due {formatDueDate(task.due_date)}</span>}
                    </div>
                  </div>
                  <div className="task-actions">
                    <button className="icon-button" onClick={() => {
                      setEditingTask(task);
                      setTaskForm({
                        title: task.title,
                        description: task.description || "",
                        status: task.status,
                        priority: task.priority,
                        due_date: toDateInput(task.due_date),
                      });
                    }}>Edit</button>
                    <button className="icon-button danger" onClick={() => deleteTask(task.id)}>Delete</button>
                  </div>
                </article>
              ))}
            </div>
          </>}
        </section>
      </div>
    </main>
  );
}
