'use client';

import { useUser, useAuth } from '@clerk/nextjs';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const { isSignedIn, user } = useUser();
  const { getToken } = useAuth();
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isSignedIn) return;

    const fetchTasks = async () => {
      try {
        const token = await getToken();
        if (!token) throw new Error('No token');

        const res = await fetch('http://127.0.0.1:8000/api/tasks', {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${await res.text()}`);
        }

        const data = await res.json();
        setTasks(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [isSignedIn, getToken]);

  if (!isSignedIn) {
    return <div className="text-center mt-10">Please sign in to view your tasks.</div>;
  }

  if (loading) return <div className="text-center mt-10">Loading tasks...</div>;
  if (error) return <div className="text-red-600 text-center mt-10">Error: {error}</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">
        Welcome, {user?.firstName || 'User'}!
      </h1>

      <h2 className="text-xl mb-4">Your Tasks</h2>

      {tasks.length === 0 ? (
        <p>No tasks found. Create one via API!</p>
      ) : (
        <ul className="space-y-4">
          {tasks.map((task) => (
            <li key={task.id} className="border p-4 rounded shadow-sm">
              <h3 className="font-semibold">{task.title}</h3>
              <p className="text-gray-600">{task.description || 'No description'}</p>
              <p className="text-sm mt-2">
                Status: <span className="font-medium">{task.status}</span>
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}













