import { Platform } from 'react-native';

// 플랫폼에 따라 API BASE URL 설정
const isAndroid = Platform.OS === 'android';
export const API_BASE_URL = isAndroid ? 'http://10.0.2.2:1500/api' : 'http://192.168.1.10:1500/api';

export async function apiGet(endpoint: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/${endpoint}`);
    if (!response.ok) throw new Error(`Error: ${response.statusText}`);
    const data = await response.json();
    console.log(`Fetched data from ${endpoint}:`, data);
    return data;
  } catch (error) {
    console.error('GET Request Error:', error);
    throw error;
  }
}

