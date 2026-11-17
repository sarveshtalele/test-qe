"use client";

import { useState, useEffect, useCallback } from "react";

export default function Page() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchTasks = useCallback(async () => {
    const res = await fetch("/tasks");
    if (res.ok) {
      const data = await res.json();
      setTasks(data);
    }
  }, []);

  useEffect(() => {
    fetchTasks().finally(() => setLoading(false));
  }, [fetchTasks]);

  async function handleAdd(e) {
    e.preventDefault();
    setError("");
    const body = { title };
    if (dueDate) body.dueDate = dueDate;
    const res = await fetch("/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      setTitle("");
      setDueDate("");
      await fetchTasks();
    } else {
      const data = await res.json();
      if (data.errors && Array.isArray(data.errors)) {
        setError(data.errors.join(", "));
      } else if (data.message) {
        setError(data.message);
      } else {
        setError("Failed to add task");
      }
    }
  }

  async function handleDone(id) {
    const res = await fetch(`/tasks/${id}`, { method: "PATCH" });
    if (res.ok) {
      await fetchTasks();
    } else {
      setError("Failed to mark task as done");
    }
  }

  async function handleDelete(id) {
    const res = await fetch(`/tasks/${id}`, { method: "DELETE" });
    if (res.ok) {
      await fetchTasks();
    } else {
      setError("Failed to delete task");
    }
  }

  if (loading) return <div>Loading...</div>;

  return (
    <main>
      <h1>Task Tracker</h1>
      <form onSubmit={handleAdd}>
        <input
          type="text"
          placeholder="Task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />
        <button type="submit">Add Task</button>
        {error && <span style={{ color: "red", marginLeft: "1em" }}>{error}</span>}
      </form>
      <ul>
        {tasks.map((task) => (
          <li key={task.id}>
            <strong>{task.title}</strong>
            {task.dueDate && <span> (Due: {task.dueDate})</span>}
            <span> [{task.status}]</span>
            {task.status === "open" && (
              <button onClick={() => handleDone(task.id)}>Done</button>
            )}
            <button onClick={() => handleDelete(task.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
