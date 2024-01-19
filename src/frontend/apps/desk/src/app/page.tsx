'use client';

import { Loader } from '@openfun/cunningham-react';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import useAuthStore from '@/auth/useAuthStore';

import Header from './Header/Header';
import { Teams } from './Teams';

export default function Home() {
  const { initAuth, authenticated, initialized } = useAuthStore();
  const { t } = useTranslation();

  useEffect(() => {
    if (initialized) {
      return;
    }

    initAuth();
  }, [initAuth, initialized]);

  if (!authenticated) {
    return <Loader />;
  }

  return (
    <main>
      <Header />
      <h1>{t('Hello Desk !')}</h1>
      <Teams />
    </main>
  );
}
