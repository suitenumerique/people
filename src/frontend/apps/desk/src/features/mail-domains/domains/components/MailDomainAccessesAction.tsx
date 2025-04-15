import { Button } from '@openfun/cunningham-react';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box } from '@/components';
import { AccessesGrid } from '@/features/mail-domains/access-management/components/AccessesGrid';

import { MailDomain, Role } from '@/features/domains';

import { ModalDomainAccessesManagement } from '@/features/mail-domains/access-management/components/ModalDomainAccessesManagement';

export const MailDomainAccessesAction = ({
  mailDomain,
  currentRole,
}: {
  mailDomain: MailDomain;
  currentRole: Role,
}) => {
  const { t } = useTranslation();

  const [isModalAccessOpen, setIsModalAccessOpen] = useState(false);

  return (
    <>
      <Box
        $direction="row"
        $justify="flex-end"
        $align="center"
      >
        <Box $display="flex"
          $direction="row"
          $align="center">
          {mailDomain?.abilities.post && (
            <Button
              style={{
                border: 'none',
                fontWeight: '500',
                marginBottom: '0px',
              }}
              color="primary-text"
              aria-label={t('Add a new access in {{name}} domain', {
                name: mailDomain?.name,
              })}
              onClick={() => {
                setIsModalAccessOpen(true);
              }}
            >
              {t('Partager les droits')}
            </Button>
          )}
        </Box>
      </Box>
      {isModalAccessOpen && mailDomain && (
        <ModalDomainAccessesManagement 
          mailDomain={mailDomain} 
          currentRole={currentRole}
          onClose={() => setIsModalAccessOpen(false)} />
      )}
    </>
  );
};