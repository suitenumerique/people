import { Loader } from '@gouvfr-lasuite/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import { useRouter } from 'next/router';
import React, { ReactElement, useState } from 'react';

import { Box } from '@/components';
import { TextErrors } from '@/components/TextErrors';
import {
  MailDomain,
  Role,
  useMailDomain,
} from '@/features/mail-domains/domains';
import { MailDomainView } from '@/features/mail-domains/domains/components/MailDomainView';
import { MainLayout } from '@/layouts';
import { NextPageWithLayout } from '@/types/next';

const MailboxesPage: NextPageWithLayout = () => {
  const router = useRouter();
  const [currentMailDomain, setCurrentMailDomain] = useState<MailDomain | null>(
    null,
  );
  const [currentRole, setCurrentRole] = useState<Role>(Role.VIEWER);

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
      const role = mailDomain.abilities.delete
        ? Role.OWNER
        : mailDomain.abilities.manage_accesses
          ? Role.ADMIN
          : Role.VIEWER;

      setCurrentRole(role);
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
      currentRole={currentRole}
      onMailDomainUpdate={setCurrentMailDomain}
    />
  );
};

MailboxesPage.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout backgroundColor="grey">{page}</MainLayout>;
};

export default MailboxesPage;
