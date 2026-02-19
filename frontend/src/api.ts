const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:5000/api';

export interface Diaper {
  id: number;
  timestamp: string;
  type: 'pee' | 'poop' | 'both';
}

export interface Feeding {
  id: number;
  start_time: string;
  end_time: string;
}

// Diaper API
export async function createDiaper(type: 'pee' | 'poop' | 'both'): Promise<Diaper> {
  const response = await fetch(`${API_BASE}/diapers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type }),
  });
  if (!response.ok) throw new Error('Failed to create diaper');
  return response.json();
}

export async function getDiapers(limit = 50): Promise<Diaper[]> {
  const response = await fetch(`${API_BASE}/diapers?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch diapers');
  return response.json();
}

export async function deleteDiaper(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/diapers/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete diaper');
}

export async function updateDiaper(id: number, type: 'pee' | 'poop' | 'both', timestamp?: string): Promise<Diaper> {
  const body: any = { type };
  if (timestamp) body.timestamp = timestamp;
  
  const response = await fetch(`${API_BASE}/diapers/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error('Failed to update diaper');
  return response.json();
}

// Feeding API
export async function createFeeding(start_time: string, end_time: string): Promise<Feeding> {
  const response = await fetch(`${API_BASE}/feedings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_time, end_time }),
  });
  if (!response.ok) throw new Error('Failed to create feeding');
  return response.json();
}

export async function getFeedings(limit = 50): Promise<Feeding[]> {
  const response = await fetch(`${API_BASE}/feedings?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch feedings');
  return response.json();
}

export async function deleteFeeding(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/feedings/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete feeding');
}

export async function updateFeeding(id: number, start_time: string, end_time: string): Promise<Feeding> {
  const response = await fetch(`${API_BASE}/feedings/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_time, end_time }),
  });
  if (!response.ok) throw new Error('Failed to update feeding');
  return response.json();
}
