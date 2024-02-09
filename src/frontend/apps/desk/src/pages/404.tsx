import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

import { Text } from '@/components';
import { NextPageWithLayout } from '@/types/next';

import MainLayout from './MainLayout';

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();

  return (
    <Text
      className="mt-xl"
      as="h1"
      $justify="center"
      $align="center"
      $theme="danger"
      $textAlign="center"
    >
      {t('404 - Page not found')}
    </Text>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout>{page}</MainLayout>;
};

export default Page;
