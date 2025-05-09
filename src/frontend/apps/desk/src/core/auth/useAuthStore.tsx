import { create } from 'zustand';

import { baseApiUrl } from '@/api';
import { terminateSupportSession } from '@/services';
import { User, getMe } from './api';

interface AuthStore {
  authenticated: boolean;
  initAuth: () => void;
  logout: () => void;
  userData?: User;
}

const initialState = {
  authenticated: false,
  userData: undefined,
};

export const useAuthStore = create<AuthStore>((set) => ({
  authenticated: initialState.authenticated,
  userData: initialState.userData,

  initAuth: () => {
    getMe()
      .then((data: User) => {
        set({ authenticated: true, userData: data });
      })
      .catch(() => {
        window.location.replace(new URL('authenticate/', baseApiUrl()).href);
      });
  },
  logout: () => {
    terminateSupportSession();
    window.location.replace(new URL('logout/', baseApiUrl()).href);
  },
}));
