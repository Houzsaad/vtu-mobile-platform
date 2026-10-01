const BASE_URL = 'http://127.0.0.1:8000/api';

export async function apiPost(endpoints, data) {
  const response = await fetch(`${BASE_URL}${endpoints}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  const result = await response.json();

  if (!response.ok) {
    throw { status: response.status, data: result };
  }

  return result;
}