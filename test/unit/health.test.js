import assert from "node:assert/strict";
import test from "node:test";

import { health } from "../../lib/health.js";

test("health returns ok status", () => {
  const result = health();
  assert.deepEqual(result, { status: "ok" });
});
