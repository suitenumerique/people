import { useAuthStore } from '@/features/auth';

export const fetchAPI = async (input: string, init?: RequestInit) => {
  const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}${input}`;
  const { token, logout } = useAuthStore.getState();

  const response = await fetch(apiUrl, {
    ...init,
    headers: {
      ...init?.headers,
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  response.status === 401 && logout();

  return response;
};
