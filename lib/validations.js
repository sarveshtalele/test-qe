export function validateCreateTask(body) {
  const errors = [];
  if (!body || typeof body.title !== "string" || body.title.trim().length === 0) {
    errors.push("title is required");
  }
  if (
    body.dueDate !== undefined &&
    body.dueDate !== null &&
    (typeof body.dueDate !== "string" || isNaN(Date.parse(body.dueDate)))
  ) {
    errors.push("dueDate must be a valid date string");
  }
  return errors;
}
