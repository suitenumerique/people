'use client';

import { useTranslation } from 'react-i18next';

import { Box } from '@/components';
import { Teams } from '@/features';

export default function Home() {
  const { t } = useTranslation();

  return (
    <Box $direction="column" className="p-b">
      <h1>{t('Hello Desk !')}</h1>
      <Teams />
    </Box>
  );
}
