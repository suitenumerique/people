import { Loader } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import { useRouter } from 'next/router';
import { ReactElement } from 'react';

import { Box } from '@/components';
import { TextErrors } from '@/components/TextErrors';
import {
  MailDomainsLayout,
  useMailDomain,
} from '@/features/mail-domains/domains';
import { MailDomainsContent } from '@/features/mail-domains/mailboxes';
import { NextPageWithLayout } from '@/types/next';

const MailboxesPage: NextPageWithLayout = () => {
  const router = useRouter();

  if (router?.query?.slug && typeof router.query.slug !== 'string') {
    throw new Error('Invalid mail domain slug');
  }

  const { slug } = router.query;

  const navigate = useNavigate();

  const {
    data: mailDomain,
    error,
    isError,
    isLoading,
  } = useMailDomain({ slug: String(slug) });

  if (error?.status === 404) {
    navigate.replace(`/404`);
    return null;
  }

  if (isError && error) {
    return <TextErrors causes={error?.cause} />;
  }

  if (isLoading) {
    return (
      <Box $align="center" $justify="center" $height="100%">
        <Loader />
      </Box>
    );
  } else {
    return mailDomain ? <MailDomainsContent mailDomain={mailDomain} /> : null;
  }
};

MailboxesPage.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default MailboxesPage;
