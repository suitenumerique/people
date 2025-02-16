import { Loader } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import { useRouter } from 'next/router';
import React, { ReactElement, useState } from 'react';

import { Box } from '@/components';
import { TextErrors } from '@/components/TextErrors';
import {
  MailDomain,
  MailDomainsLayout,
  useMailDomain,
} from '@/features/mail-domains/domains';
import { MailDomainView } from '@/features/mail-domains/domains/components/MailDomainView';
import { NextPageWithLayout } from '@/types/next';

const MailboxesPage: NextPageWithLayout = () => {
  const router = useRouter();
  const [currentMailDomain, setCurrentMailDomain] = useState<MailDomain | null>(
    null,
  );

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

  // Update currentMailDomain when mailDomain changes
  React.useEffect(() => {
    if (mailDomain) {
      setCurrentMailDomain(mailDomain);
    }
  }, [mailDomain]);

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
  }

  if (!currentMailDomain) {
    return null;
  }

  return (
    <MailDomainView
      mailDomain={currentMailDomain}
      onMailDomainUpdate={setCurrentMailDomain}
    />
  );
};

MailboxesPage.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default MailboxesPage;
