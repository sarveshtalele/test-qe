import assert from "node:assert/strict";
import test from "node:test";

import { health } from "../../lib/health.js";

test("health reports ok with taskCount", () => {
  const result = health();
  assert.equal(result.status, "ok");
  assert.equal(typeof result.taskCount, "number");
});
