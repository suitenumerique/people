import { ReactElement } from 'react';

import { Box } from '@/components';
import { CardCreateTeam } from '@/features/teams';
import { NextPageWithLayout } from '@/types/next';

import TeamLayout from './TeamLayout';

const Page: NextPageWithLayout = () => {
  return (
    <Box className="p-l" $justify="center" $align="start" $height="inherit">
      <CardCreateTeam />
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
