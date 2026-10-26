import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

import App from "../App";
import { AuthProvider } from "../auth";

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal("fetch", vi.fn(async (url) => {
    if (url.endsWith("/auth/login")) {
      return { ok: true, status: 200, json: async () => ({ access_token: "test-token" }) };
    }
    if (url.endsWith("/projects")) {
      return { ok: true, status: 200, json: async () => [] };
    }
    if (url.endsWith("/dashboard/stats")) {
      return {
        ok: true,
        status: 200,
        json: async () => ({ total_tasks: 0, overdue_tasks: 0, by_status: {}, by_priority: {} }),
      };
    }
    throw new Error(`Unexpected request: ${url}`);
  }));
});

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

it("signs in and shows the dashboard", async () => {
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={["/login"]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  );

  await user.type(screen.getByLabelText("Email"), "ada@example.com");
  await user.type(screen.getByLabelText("Password"), "a-safe-test-password");
  await user.click(screen.getByRole("button", { name: "Sign in" }));

  expect(await screen.findByRole("heading", { name: "My workspace" })).toBeInTheDocument();
  expect(localStorage.getItem("taskflow_access_token")).toBe("test-token");
});

it("clears an expired token and returns to sign in", async () => {
  localStorage.setItem("taskflow_access_token", "expired-token");
  vi.stubGlobal("fetch", vi.fn(async () => ({
    ok: false,
    status: 401,
    json: async () => ({ error: { message: "Invalid or expired token" } }),
  })));

  render(
    <MemoryRouter initialEntries={["/"]}>
      <AuthProvider><App /></AuthProvider>
    </MemoryRouter>,
  );

  expect(await screen.findByRole("heading", { name: "Welcome back" })).toBeInTheDocument();
  expect(localStorage.getItem("taskflow_access_token")).toBeNull();
});

it("shows an error instead of crashing when the task list is null", async () => {
  localStorage.setItem("taskflow_access_token", "test-token");
  vi.stubGlobal("fetch", vi.fn(async (url) => {
    if (url.endsWith("/projects")) {
      return { ok: true, status: 200, json: async () => [{ id: 1, name: "Demo" }] };
    }
    if (url.endsWith("/dashboard/stats")) {
      return { ok: true, status: 200, json: async () => ({ total_tasks: 0 }) };
    }
    if (url.includes("/projects/1/tasks?")) {
      return { ok: true, status: 200, json: async () => null };
    }
    throw new Error(`Unexpected request: ${url}`);
  }));

  render(
    <MemoryRouter initialEntries={["/"]}>
      <AuthProvider><App /></AuthProvider>
    </MemoryRouter>,
  );

  expect(await screen.findByRole("alert")).toHaveTextContent("invalid task list");
  expect(screen.getByText("No matching tasks.")).toBeInTheDocument();
});
