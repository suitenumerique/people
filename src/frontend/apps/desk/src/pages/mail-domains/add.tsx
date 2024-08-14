import React, { ReactElement } from 'react';

import { Box } from '@/components';
import { MailDomainsLayout } from '@/features/mail-domains';
import { ModalCreateMailDomain } from '@/features/mail-domains/components/ModalAddMailDomain';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  return (
    <Box $padding="large" $height="inherit">
      <ModalCreateMailDomain />
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default Page;
