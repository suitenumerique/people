import { create } from 'zustand';

import { getConfig } from './api';
import { Config } from './types';

interface ConfStore {
  config?: Config;
  initConfig: () => void;
}

const initialState = {
  config: undefined,
};

export const useConfigStore = create<ConfStore>((set) => ({
  config: initialState.config,
  initConfig: () => {
    void getConfig()
      .then((config: Config) => {
        set({ config });
      })
      .catch(() => {
        console.error('Failed to fetch config data');
      });
  },
}));
