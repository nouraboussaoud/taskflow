export function ErrorMessage({ message }) {
  return message ? <p className="notice notice-error" role="alert">{message}</p> : null;
}

export function Loading({ label = "Loading…" }) {
  return <p className="loading">{label}</p>;
}

export function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{status.replace("_", " ")}</span>;
}

export function PriorityBadge({ priority }) {
  return <span className={`priority priority-${priority}`}>{priority}</span>;
}
