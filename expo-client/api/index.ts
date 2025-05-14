export const API_BASE_URL = 'http://10.0.2.2:1500';

export async function apiGet(endpoint: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/${endpoint}`);
    if (!response.ok) throw new Error(`Error: ${response.statusText}`);
    return await response.json();
  } catch (error) {
    console.error('GET Request Error:', error);
    throw error;
  }
}