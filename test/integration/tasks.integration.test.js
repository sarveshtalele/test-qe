import assert from "node:assert/strict";
import test from "node:test";

// Integration tests for task endpoints using direct handler calls
// We simulate requests via the Next.js route handlers

import { createRequire } from "module";
const require = createRequire(import.meta.url);

function freshStore() {
  delete require.cache[require.resolve("../../lib/store.js")];
  return require("../../lib/store.js");
}

// Helper to call a handler with a simulated request
export function simulateRequest(handler, { method, body, params } = {}) {
  const req = {
    method,
    json: async () => body,
  };
  const context = { params: params || {} };
  // For async handlers
  return handler(req, context);
}

test("POST /tasks creates a task and returns 201", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const res = await simulateRequest(POST, {
    method: "POST",
    body: { title: "Integration task" },
  });
  assert.equal(res.status, 201);
  const data = await res.json();
  assert.equal(data.title, "Integration task");
  assert.equal(data.status, "open");
  assert.equal(typeof data.id, "string");
});

test("POST /tasks with optional dueDate returns 201", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const res = await simulateRequest(POST, {
    method: "POST",
    body: { title: "With date", dueDate: "2025-12-31" },
  });
  assert.equal(res.status, 201);
  const data = await res.json();
  assert.equal(data.dueDate, "2025-12-31");
});

test("POST /tasks with missing title returns 400", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const res = await simulateRequest(POST, {
    method: "POST",
    body: {},
  });
  assert.equal(res.status, 400);
  const data = await res.json();
  assert.deepEqual(data.errors, ["title is required"]);
});

test("GET /tasks lists tasks newest first", async () => {
  freshStore();
  const { POST, GET } = await import("../../app/tasks/route.js");
  const { tasks } = await import("../../lib/store.js");
  await simulateRequest(POST, { method: "POST", body: { title: "First" } });
  await simulateRequest(POST, { method: "POST", body: { title: "Second" } });
  // Set createdAt so that Second is earlier than First
  tasks[0].createdAt = "2025-01-01T00:00:00.000Z";
  tasks[1].createdAt = "2025-01-02T00:00:00.000Z";
  const res = await simulateRequest(GET, { method: "GET" });
  assert.equal(res.status, 200);
  const list = await res.json();
  assert.equal(list.length, 2);
  assert.equal(list[0].title, "Second");
  assert.equal(list[1].title, "First");
});

test("PATCH /tasks/:id/complete marks task as done and returns 200", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const postRes = await simulateRequest(POST, {
    method: "POST",
    body: { title: "Complete me" },
  });
  const task = await postRes.json();
  const { PATCH } = await import("../../app/tasks/[id]/route.js");
  const res = await simulateRequest(PATCH, {
    method: "PATCH",
    body: {},
    params: { id: task.id },
  });
  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(data.status, "done");
});

test("PATCH /tasks/:id/complete on already done task returns 409", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const postRes = await simulateRequest(POST, {
    method: "POST",
    body: { title: "Already done" },
  });
  const task = await postRes.json();
  const { PATCH } = await import("../../app/tasks/[id]/route.js");
  // First completion
  await simulateRequest(PATCH, {
    method: "PATCH",
    body: {},
    params: { id: task.id },
  });
  // Second completion
  const res = await simulateRequest(PATCH, {
    method: "PATCH",
    body: {},
    params: { id: task.id },
  });
  assert.equal(res.status, 409);
  const data = await res.json();
  assert.equal(data.message, "task is already done");
});

test("PATCH /tasks/:id/complete with nonexistent id returns 404", async () => {
  freshStore();
  const { PATCH } = await import("../../app/tasks/[id]/route.js");
  const res = await simulateRequest(PATCH, {
    method: "PATCH",
    body: {},
    params: { id: "nonexistent" },
  });
  assert.equal(res.status, 404);
  const data = await res.json();
  assert.equal(data.message, "task not found");
});

test("DELETE /tasks/:id deletes and returns 204", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const postRes = await simulateRequest(POST, {
    method: "POST",
    body: { title: "Delete me" },
  });
  const task = await postRes.json();
  const { DELETE } = await import("../../app/tasks/[id]/route.js");
  const res = await simulateRequest(DELETE, {
    method: "DELETE",
    body: {},
    params: { id: task.id },
  });
  assert.equal(res.status, 204);
  const body = await res.text();
  assert.equal(body, "");
});

test("DELETE /tasks/:id with nonexistent id returns 404", async () => {
  freshStore();
  const { DELETE } = await import("../../app/tasks/[id]/route.js");
  const res = await simulateRequest(DELETE, {
    method: "DELETE",
    body: {},
    params: { id: "nonexistent" },
  });
  assert.equal(res.status, 404);
  const data = await res.json();
  assert.equal(data.message, "task not found");
});

test("Deleted task no longer appears in GET /tasks", async () => {
  freshStore();
  const { POST, GET } = await import("../../app/tasks/route.js");
  const postRes = await simulateRequest(POST, {
    method: "POST",
    body: { title: "Temp task" },
  });
  const task = await postRes.json();
  const { DELETE } = await import("../../app/tasks/[id]/route.js");
  await simulateRequest(DELETE, {
    method: "DELETE",
    body: {},
    params: { id: task.id },
  });
  const getRes = await simulateRequest(GET, { method: "GET" });
  const list = await getRes.json();
  assert.equal(list.find((t) => t.id === task.id), undefined);
});
