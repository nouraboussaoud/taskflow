import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { api } from "../api";
import { useAuth } from "../auth";
import { ErrorMessage } from "../components";

export function Login() {
  const { token, signIn } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (token) return <Navigate to="/" replace />;

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const result = await api("/auth/login", { method: "POST", body: { email, password } });
      signIn(result.access_token);
      navigate("/");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">TaskFlow</p>
        <h1>Welcome back</h1>
        <p className="muted">Sign in to manage your projects and tasks.</p>
        {location.state?.message && <p className="notice notice-success">{location.state.message}</p>}
        <ErrorMessage message={error} />
        <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
        <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        <button type="submit" disabled={submitting}>{submitting ? "Signing in…" : "Sign in"}</button>
        <p className="muted">No account? <Link to="/register">Create one</Link></p>
      </form>
    </main>
  );
}
