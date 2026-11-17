let nextId = 1;
export const tasks = [];

export function addTask(task) {
  const newTask = {
    id: String(nextId++),
    title: task.title,
    dueDate: task.dueDate || null,
    status: "open",
    createdAt: new Date().toISOString(),
  };
  tasks.push(newTask);
  return newTask;
}

export function listTasks() {
  return [...tasks].sort(
    (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
  );
}

export function findTask(id) {
  return tasks.find((t) => t.id === id) || null;
}

export function updateTask(id, updates) {
  const idx = tasks.findIndex((t) => t.id === id);
  if (idx === -1) return null;
  tasks[idx] = { ...tasks[idx], ...updates };
  return tasks[idx];
}

export function deleteTask(id) {
  const idx = tasks.findIndex((t) => t.id === id);
  if (idx === -1) return false;
  tasks.splice(idx, 1);
  return true;
}
