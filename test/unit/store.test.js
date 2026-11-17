import assert from "node:assert/strict";
import test from "node:test";

import { addTask, listTasks, findTask, updateTask, deleteTask, tasks } from "../../lib/store.js";

// Reset store in-place
function freshStore() {
  tasks.length = 0;
  return { addTask, listTasks, findTask, updateTask, deleteTask, tasks };
}

test("addTask creates a task with correct fields", () => {
  const { addTask, tasks } = freshStore();
  const task = addTask({ title: "Test task" });
  assert.equal(typeof task.id, "string");
  assert.equal(task.title, "Test task");
  assert.equal(task.dueDate, null);
  assert.equal(task.status, "open");
  assert.equal(typeof task.createdAt, "string");
  assert.equal(tasks.length, 1);
});

test("addTask accepts optional dueDate", () => {
  const { addTask } = freshStore();
  const task = addTask({ title: "Task with date", dueDate: "2025-12-31" });
  assert.equal(task.dueDate, "2025-12-31");
});

test("listTasks returns tasks newest first", () => {
  const { addTask, listTasks, tasks: storeTasks } = freshStore();
  addTask({ title: "First" });
  addTask({ title: "Second" });
  // Set createdAt so that Second is earlier than First
  storeTasks[0].createdAt = "2025-01-01T00:00:00.000Z";
  storeTasks[1].createdAt = "2025-01-02T00:00:00.000Z";
  const list = listTasks();
  assert.equal(list.length, 2);
  assert.equal(list[0].title, "Second");
  assert.equal(list[1].title, "First");
});

test("findTask returns task or null", () => {
  const { addTask, findTask } = freshStore();
  const task = addTask({ title: "Find me" });
  assert.notEqual(findTask(task.id), null);
  assert.equal(findTask("nonexistent"), null);
});

test("updateTask modifies task and returns it", () => {
  const { addTask, updateTask } = freshStore();
  const task = addTask({ title: "Update me" });
  const updated = updateTask(task.id, { status: "done" });
  assert.notEqual(updated, null);
  assert.equal(updated.status, "done");
  assert.equal(updated.title, "Update me");
});

test("updateTask returns null for nonexistent id", () => {
  const { updateTask } = freshStore();
  assert.equal(updateTask("bad-id", { status: "done" }), null);
});

test("deleteTask removes task and returns true", () => {
  const { addTask, deleteTask, findTask } = freshStore();
  const task = addTask({ title: "Delete me" });
  assert.equal(deleteTask(task.id), true);
  assert.equal(findTask(task.id), null);
});

test("deleteTask returns false for nonexistent id", () => {
  const { deleteTask } = freshStore();
  assert.equal(deleteTask("bad-id"), false);
});
