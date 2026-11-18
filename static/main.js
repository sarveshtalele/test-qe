// Web UI for task-tracker

const apiBase = '';

async function fetchTasks() {
  const res = await fetch(`${apiBase}/tasks`);
  return res.json();
}

async function createTask(title, dueDate) {
  const body = { title };
  if (dueDate) {
    body.due_date = dueDate;
  }
  const res = await fetch(`${apiBase}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errBody = await res.json();
    throw new Error(errBody.detail || 'Unknown error');
  }
  return res.json();
}

async function completeTask(taskId) {
  const res = await fetch(`${apiBase}/tasks/${taskId}/complete`, { method: 'PUT' });
  if (!res.ok) {
    const errBody = await res.json();
    throw new Error(errBody.detail || 'Unknown error');
  }
  return res.json();
}

async function deleteTask(taskId) {
  await fetch(`${apiBase}/tasks/${taskId}`, { method: 'DELETE' });
}

function showError(msg) {
  const el = document.getElementById('error-message');
  el.textContent = msg;
  el.style.display = 'block';
}

function clearError() {
  const el = document.getElementById('error-message');
  el.textContent = '';
  el.style.display = 'none';
}

function renderTask(task) {
  const li = document.createElement('li');
  li.setAttribute('data-testid', 'task-item');
  li.setAttribute('role', 'item');

  const titleSpan = document.createElement('span');
  titleSpan.setAttribute('data-testid', 'task-title-text');
  titleSpan.setAttribute('role', 'text');
  titleSpan.textContent = task.title;

  const dueSpan = document.createElement('span');
  dueSpan.setAttribute('data-testid', 'task-due-date-text');
  dueSpan.setAttribute('role', 'text');
  dueSpan.textContent = task.due_date || '';

  const statusSpan = document.createElement('span');
  statusSpan.setAttribute('data-testid', 'task-status-text');
  statusSpan.setAttribute('role', 'text');
  statusSpan.textContent = task.status;

  li.appendChild(titleSpan);
  li.appendChild(document.createTextNode(' — '));
  li.appendChild(dueSpan);
  li.appendChild(document.createTextNode(' ('));
  li.appendChild(statusSpan);
  li.appendChild(document.createTextNode(')'));

  const doneBtn = document.createElement('button');
  doneBtn.setAttribute('data-testid', 'done-button');
  doneBtn.setAttribute('role', 'button');
  doneBtn.textContent = 'Done';
  doneBtn.addEventListener('click', async () => {
    try {
      clearError();
      await completeTask(task.id);
      loadTasks();
    } catch (e) {
      showError(e.message);
    }
  });
  li.appendChild(doneBtn);

  const deleteBtn = document.createElement('button');
  deleteBtn.setAttribute('data-testid', 'delete-button');
  deleteBtn.setAttribute('role', 'button');
  deleteBtn.textContent = 'Delete';
  deleteBtn.addEventListener('click', async () => {
    try {
      clearError();
      await deleteTask(task.id);
      loadTasks();
    } catch (e) {
      showError(e.message);
    }
  });
  li.appendChild(deleteBtn);

  return li;
}

async function loadTasks() {
  clearError();
  const tasks = await fetchTasks();
  const list = document.getElementById('task-list');
  list.innerHTML = '';
  tasks.forEach(task => {
    list.appendChild(renderTask(task));
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadTasks();

  const form = document.getElementById('task-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError();
    const titleInput = document.getElementById('title');
    const dueInput = document.getElementById('due_date');
    const title = titleInput.value.trim();
    if (!title) return;
    try {
      await createTask(title, dueInput.value.trim() || undefined);
      titleInput.value = '';
      dueInput.value = '';
      loadTasks();
    } catch (err) {
      showError(err.message);
      // Keep what was typed (no reset)
    }
  });
});
