import { findTask, updateTask, deleteTask } from "../../../lib/store.js";

export const dynamic = "force-dynamic";

export async function PATCH(request, { params }) {
  const { id } = await params;
  const task = findTask(id);
  if (!task) {
    return Response.json({ message: "task not found" }, { status: 404 });
  }
  if (task.status === "done") {
    return Response.json({ message: "task is already done" }, { status: 409 });
  }
  const updated = updateTask(id, { status: "done" });
  return Response.json(updated, { status: 200 });
}

export async function DELETE(request, { params }) {
  const { id } = await params;
  const task = findTask(id);
  if (!task) {
    return Response.json({ message: "task not found" }, { status: 404 });
  }
  deleteTask(id);
  return new Response(null, { status: 204 });
}
