import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { api } from "../api";
import { useAuth } from "../auth";
import { ErrorMessage } from "../components";

export function Register() {
  const { token } = useAuth();
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
      await api("/auth/register", { method: "POST", body: { email, password } });
      navigate("/login", { state: { message: "Account created. Please sign in." } });
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
        <h1>Create your account</h1>
        <p className="muted">Use at least 12 characters for your password.</p>
        <ErrorMessage message={error} />
        <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
        <label>Password<input type="password" minLength="12" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        <button type="submit" disabled={submitting}>{submitting ? "Creating…" : "Create account"}</button>
        <p className="muted">Already registered? <Link to="/login">Sign in</Link></p>
      </form>
    </main>
  );
}
