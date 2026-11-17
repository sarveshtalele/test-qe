import { addTask, listTasks } from "../../lib/store.js";
import { validateCreateTask } from "../../lib/validations.js";

export const dynamic = "force-dynamic";

export async function POST(request) {
  const body = await request.json().catch(() => null);
  const errors = validateCreateTask(body);
  if (errors.length > 0) {
    return Response.json({ errors }, { status: 400 });
  }
  const task = addTask({ title: body.title.trim(), dueDate: body.dueDate || null });
  return Response.json(task, { status: 201 });
}

export function GET() {
  return Response.json(listTasks());
}
