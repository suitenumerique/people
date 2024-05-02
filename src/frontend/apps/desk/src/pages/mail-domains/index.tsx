import { ReactElement } from 'react';

import { MailDomainsLayout } from '@/features/mail-domains';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  return null;
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default Page;
