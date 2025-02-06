import { Button } from '@openfun/cunningham-react';
import { useRouter } from 'next/router';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, Text, Card } from '@/components';
import { useAuthStore } from '@/core/auth';
import { MainLayout } from '@/layouts';
import { NextPageWithLayout } from '@/types/next';
import { MailDomainsListView } from '@/features/mail-domains/domains/components/MailDomainsListView';

const StyledButton = styled(Button)`
  width: fit-content;
`;

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { userData } = useAuthStore();
  const can_create = userData?.abilities?.mailboxes.can_create;
  const router = useRouter();

  return (
    <Box
      $position="relative"
      $width="100%"
      $direction="row"
      $maxWidth="960px"
      $maxHeight="calc(100vh - 52px - 1rem)"
      $align="center"
      $margin="20px auto"
      $padding="0 10px"
      $css={`
        overflow-x: hidden;
        overflow-y: auto;
      `}
    >
    <Card
        data-testid="regie-grid"
        $height="100%"
        $justify="center"
        $width="100%"
        $css={`
          overflow-x: hidden;
          overflow-y: auto;
        `}
        $padding={{
          top: 'md',
          bottom: 'md',
          horizontal: 'md'
        }}
      >
       <Text
        as="h2"
        $weight="700"
        $size="h4"
        $variation="1000"
        $margin={{ top: '0px', bottom: '20px' }}
        >
        Domaines de l’organisation
        </Text>

        <Box $margin={{ top: '0px', bottom: '20px' }}>
      {can_create && (
        <StyledButton onClick={() => void router.push('/mail-domains/add')}>
          {t('Add a mail domain')}
        </StyledButton>
      )}
      </Box>

      {!can_create && <Text>{t('Click on mailbox to view details')}</Text>}
      <MailDomainsListView />
      </Card>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout backgroundColor="grey">{page}</MainLayout>;
};

export default Page;
