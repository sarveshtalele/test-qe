import { tasks } from "./store.js";

export function health() {
  return { status: "ok", taskCount: tasks.length };
}
