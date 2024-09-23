import React, { ReactElement } from 'react';

import { Box } from '@/components';
import {
  MailDomainsLayout,
  ModalAddMailDomain,
} from '@/features/mail-domains/domains';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  return (
    <Box $padding="large" $height="inherit">
      <ModalAddMailDomain />
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default Page;
