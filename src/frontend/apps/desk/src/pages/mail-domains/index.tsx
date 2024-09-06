import { Button } from '@openfun/cunningham-react';
import { useRouter } from 'next/router';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box } from '@/components';
import { MailDomainsLayout } from '@/features/mail-domains';
import { NextPageWithLayout } from '@/types/next';

const StyledButton = styled(Button)`
  width: fit-content;
`;

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();

  const router = useRouter();

  return (
    <Box $align="center" $justify="center" $height="inherit">
      <StyledButton onClick={() => void router.push('/mail-domains/add')}>
        {t('Add a mail domain')}
      </StyledButton>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default Page;
