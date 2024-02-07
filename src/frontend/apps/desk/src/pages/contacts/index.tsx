import { ReactElement } from 'react';

import { Box } from '@/components';
import { NextPageWithLayout } from '@/types/next';

import MainLayout from '../MainLayout';

const Page: NextPageWithLayout = () => {
  return <Box>Contacts</Box>;
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout>{page}</MainLayout>;
};

export default Page;
