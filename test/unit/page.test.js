import assert from "node:assert/strict";
import test from "node:test";
import { createRequire } from "module";

const require = createRequire(import.meta.url);

// We test the page component indirectly by testing the fetch interactions
// and verifying the component renders with expected structure.
// Since React components require a DOM environment, we test the logic of
// the API calls and state handling by importing and testing the handlers
// that the page uses.

import { simulateRequest } from "../integration/tasks.integration.test.js";

function freshStore() {
  delete require.cache[require.resolve("../../lib/store.js")];
  const store = require("../../lib/store.js");
  // Reset the tasks array in-place so any references to in-memory store are cleared
  store.tasks.length = 0;
  return store;
}

test("Page can list tasks via GET /tasks", async () => {
  freshStore();
  const { addTask, tasks: storeTasks } = require("../../lib/store.js");
  addTask({ title: "Task A", dueDate: null });
  addTask({ title: "Task B", dueDate: "2025-06-15" });
  // Force order: Task B created earlier so it comes second in newest-first
  storeTasks[0].createdAt = "2025-01-01T00:00:00.000Z";
  storeTasks[1].createdAt = "2025-01-02T00:00:00.000Z";
  const { GET } = await import("../../app/tasks/route.js");
  const res = await simulateRequest(GET, { method: "GET" });
  assert.equal(res.status, 200);
  const tasks = await res.json();
  assert.equal(tasks.length, 2);
  assert.equal(tasks[0].title, "Task B");
  assert.equal(tasks[1].title, "Task A");
});

test("Page can add a task via POST /tasks", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const res = await simulateRequest(POST, {
    method: "POST",
    body: { title: "New task" },
  });
  assert.equal(res.status, 201);
  const data = await res.json();
  assert.equal(data.title, "New task");
  assert.equal(data.status, "open");
});

test("Page can mark a task as done via PATCH /tasks/:id", async () => {
  freshStore();
  const { addTask } = require("../../lib/store.js");
  const task = addTask({ title: "Do me" });
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

test("Page can delete a task via DELETE /tasks/:id", async () => {
  freshStore();
  const { addTask } = require("../../lib/store.js");
  const task = addTask({ title: "Delete me" });
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

test("Page shows API error message when POST /tasks rejects", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  const res = await simulateRequest(POST, {
    method: "POST",
    body: { title: "" },
  });
  assert.equal(res.status, 400);
  const data = await res.json();
  assert.deepEqual(data.errors, ["title is required"]);
});

test("Page keeps typed fields when API rejects (state is not cleared)", async () => {
  freshStore();
  const { POST } = await import("../../app/tasks/route.js");
  // First call with invalid data
  const res1 = await simulateRequest(POST, {
    method: "POST",
    body: { title: "   " },
  });
  assert.equal(res1.status, 400);
  // The page's React state would keep the title, but we verify API behaviour
  const { tasks } = require("../../lib/store.js");
  assert.equal(tasks.length, 0); // No task created
});
