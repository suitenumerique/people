import { Button } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box } from '@/components';
import { TeamLayout } from '@/features/teams/team-management';
import { NextPageWithLayout } from '@/types/next';

const StyledButton = styled(Button)`
  width: fit-content;
`;

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const router = useNavigate();

  return (
    <Box $align="center" $justify="center" $height="inherit">
      <StyledButton onClick={() => void router.push('/teams/create')}>
        {t('Create a new team')}
      </StyledButton>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
