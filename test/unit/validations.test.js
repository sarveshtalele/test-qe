import assert from "node:assert/strict";
import test from "node:test";

import { validateCreateTask } from "../../lib/validations.js";

test("validateCreateTask returns empty for valid title without dueDate", () => {
  const errors = validateCreateTask({ title: "My task" });
  assert.deepEqual(errors, []);
});

test("validateCreateTask returns empty for valid title with valid dueDate", () => {
  const errors = validateCreateTask({ title: "Task", dueDate: "2025-06-01" });
  assert.deepEqual(errors, []);
});

test("validateCreateTask returns empty for null dueDate", () => {
  const errors = validateCreateTask({ title: "Task", dueDate: null });
  assert.deepEqual(errors, []);
});

test("validateCreateTask returns error for missing title", () => {
  const errors = validateCreateTask({});
  assert.deepEqual(errors, ["title is required"]);
});

test("validateCreateTask returns error for empty title", () => {
  const errors = validateCreateTask({ title: "   " });
  assert.deepEqual(errors, ["title is required"]);
});

test("validateCreateTask returns error for invalid dueDate", () => {
  const errors = validateCreateTask({ title: "Task", dueDate: "not-a-date" });
  assert.deepEqual(errors, ["dueDate must be a valid date string"]);
});

test("validateCreateTask returns multiple errors if both title and dueDate invalid", () => {
  const errors = validateCreateTask({ dueDate: "bad" });
  assert.equal(errors.length, 2);
  assert.ok(errors.includes("title is required"));
  assert.ok(errors.includes("dueDate must be a valid date string"));
});
