import React, { ReactElement } from 'react';

import { Box } from '@/components';
import {
  ModalAddMailDomain,
} from '@/features/mail-domains/domains';
import { MainLayout } from '@/layouts';

import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  return (
    <Box $padding="large" $height="inherit">
      <ModalAddMailDomain />
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout>{page}</MainLayout>;
};

export default Page;
