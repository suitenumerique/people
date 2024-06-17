import { Loader } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import { useRouter } from 'next/router';
import { ReactElement } from 'react';

import { Box } from '@/components';
import { TextErrors } from '@/components/TextErrors';
import { MailDomainsContent, MailDomainsLayout } from '@/features/mail-domains';
import { useMailDomain } from '@/features/mail-domains/api/useMailDomain';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const router = useRouter();

  if (router?.query?.slug && typeof router.query.slug !== 'string') {
    throw new Error('Invalid mail domain slug');
  }

  const { slug } = router.query;

  const navigate = useNavigate();

  const {
    data: mailDomain,
    error: error,
    isError,
    isLoading: isLoading,
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

Page.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default Page;
