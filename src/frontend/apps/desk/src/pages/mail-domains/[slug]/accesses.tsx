import { Loader } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import { useRouter } from 'next/router';
import { ReactElement } from 'react';

import { Box } from '@/components';
import { TextErrors } from '@/components/TextErrors';
import { AccessesContent } from '@/features/mail-domains/access-management';
import {
  MailDomainsLayout,
  Role,
  useMailDomain,
} from '@/features/mail-domains/domains';
import { NextPageWithLayout } from '@/types/next';

const MailDomainAccessesPage: NextPageWithLayout = () => {
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
  }

  if (mailDomain) {
    const currentRole = mailDomain.abilities.delete
      ? Role.OWNER
      : mailDomain.abilities.manage_accesses
        ? Role.ADMIN
        : Role.VIEWER;

    return (
      <AccessesContent mailDomain={mailDomain} currentRole={currentRole} />
    );
  }

  return null;
};

MailDomainAccessesPage.getLayout = function getLayout(page: ReactElement) {
  return <MailDomainsLayout>{page}</MailDomainsLayout>;
};

export default MailDomainAccessesPage;
