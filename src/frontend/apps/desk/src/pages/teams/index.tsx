import { Button } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, Text } from '@/components';
import { useAuthStore } from '@/core/auth';
import { TeamLayout } from '@/features/teams/team-management';
import { NextPageWithLayout } from '@/types/next';

const StyledButton = styled(Button)`
  width: fit-content;
`;

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const router = useNavigate();
  const { userData } = useAuthStore();
  const can_create = userData?.abilities?.teams.can_create ?? false;

  return (
    <Box $align="center" $justify="center" $height="inherit">
      {can_create && (
        <StyledButton onClick={() => void router.push('/teams/create')}>
          {t('Create a new team')}
        </StyledButton>
      )}
      {!can_create && <Text>{t('Click on team to view details')}</Text>}
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
