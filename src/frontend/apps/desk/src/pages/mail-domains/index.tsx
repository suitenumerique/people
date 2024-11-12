import { Button } from '@openfun/cunningham-react';
import { useRouter } from 'next/router';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, Text } from '@/components';
import { useAuthStore } from '@/core/auth';
import { MailDomainsLayout } from '@/features/mail-domains/domains';
import { NextPageWithLayout } from '@/types/next';

const StyledButton = styled(Button)`
  width: fit-content;
`;

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { userData } = useAuthStore();
  const can_create = userData?.abilities?.mailboxes.can_create;
  const router = useRouter();

  return (
    <Box $align="center" $justify="center" $height="inherit">
      {can_create && (
        <StyledButton onClick={() => void router.push('/mail-domains/add')}>
          {t('Add a mail domain')}
        </StyledButton>
      )}
      {!can_create && <Text>{t('Click on mailbox to view details')}</Text>}
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default Page;
