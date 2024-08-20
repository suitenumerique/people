import { fetchAPI } from '@/api';

import { Config } from '../types';

export const getConfig = async (): Promise<Config> => {
  const response = await fetchAPI(`config/`);
  if (!response.ok) {
    throw new Error(`Couldn't fetch conf data: ${response.statusText}`);
  }
  return response.json() as Promise<Config>;
};
