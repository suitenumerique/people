import { create } from 'zustand';

import { initKeycloak } from './keycloak';

interface AuthStore {
  authenticated: boolean;
  initAuth: () => void;
  initialized: boolean;
  logout: () => void;
  token: string | null;
}

const initialState = {
  authenticated: false,
  initialized: false,
  token: null,
};

export const useAuthStore = create<AuthStore>((set) => ({
  authenticated: initialState.authenticated,
  initialized: initialState.initialized,
  token: initialState.token,

  initAuth: () =>
    set((state) => {
      if (process.env.NEXT_PUBLIC_KEYCLOAK_LOGIN && !state.initialized) {
        initKeycloak((token) => set({ authenticated: true, token }));
        return { initialized: true };
      }

      /**
       * TODO: Implement OIDC production authentication
       */

      return {};
    }),

  logout: () => {
    set(initialState);
  },
}));
