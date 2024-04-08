import { ReactElement } from 'react';

import { MailContent, MailLayout } from '@/features/mails';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  return <MailContent />;
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MailLayout>{page}</MailLayout>;
};

export default Page;
