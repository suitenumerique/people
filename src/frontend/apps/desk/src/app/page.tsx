'use client';

import { Loader } from '@openfun/cunningham-react';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import useAuthStore from '@/auth/useAuthStore';
import { Box } from '@/components';

import Header, { HEADER_HEIGHT } from './Header/Header';
import { Teams } from './Teams';
import { MENU_WIDTH, Menu } from './menu';

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
      <Box $css={`margin-top:${HEADER_HEIGHT}`}>
        <Menu />
        <Box
          $css={`margin-left:${MENU_WIDTH}`}
          $direction="column"
          $height="300vh"
          className="p-b"
        >
          <h1>{t('Hello Desk !')}</h1>
          <Teams />
        </Box>
      </Box>
    </main>
  );
}
