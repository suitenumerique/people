import { fetchAPI } from '@/api';

export const logout = async () => {
  await fetchAPI(`logout/`, {
    method: 'POST',
    redirect: 'manual',
  });
};
