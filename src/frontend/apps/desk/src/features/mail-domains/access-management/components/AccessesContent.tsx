import { Button } from '@openfun/cunningham-react';
import { useRouter } from 'next/navigation';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { AccessesGrid } from '@/features/mail-domains/access-management/components/AccessesGrid';
import MailDomainsLogo from '@/features/mail-domains/assets/mail-domains-logo.svg';

import { MailDomain, Role } from '../../domains';

export const AccessesContent = ({
  mailDomain,
  currentRole,
}: {
  mailDomain: MailDomain;
  currentRole: Role;
}) => (
  <>
    <TopBanner mailDomain={mailDomain} />
    <AccessesGrid mailDomain={mailDomain} currentRole={currentRole} />
  </>
);

const TopBanner = ({ mailDomain }: { mailDomain: MailDomain }) => {
  const router = useRouter();
  const { t } = useTranslation();

  return (
    <Box
      $direction="column"
      $margin={{ all: 'big', bottom: 'tiny' }}
      $gap="1rem"
    >
      <Box
        $direction="row"
        $align="center"
        $gap="2.25rem"
        $justify="space-between"
      >
        <Box $direction="row" $margin="none" $gap="0.5rem">
          <MailDomainsLogo aria-hidden="true" />
          <Text $margin="none" as="h3" $size="h3">
            {mailDomain?.name}
          </Text>
        </Box>
      </Box>

      <Box $direction="row" $justify="flex-end">
        <Box $display="flex" $direction="row" $gap="8rem">
          {mailDomain?.abilities?.manage_accesses && (
            <Button
              color="tertiary"
              aria-label={t('Manage {{name}} domain mailboxes', {
                name: mailDomain?.name,
              })}
              onClick={() => router.push(`/mail-domains/${mailDomain.slug}/`)}
            >
              {t('Manage mailboxes')}
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};
