import type { ReactElement } from 'react';

import { NextPageWithLayout } from '@/types/next';

import Teams from './teams/';
import TeamLayout from './teams/TeamLayout';

const Page: NextPageWithLayout = () => {
  return <Teams />;
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
