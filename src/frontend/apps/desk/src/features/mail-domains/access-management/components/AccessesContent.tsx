import { Button } from '@openfun/cunningham-react';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box } from '@/components';
import { AccessesGrid } from '@/features/mail-domains/access-management/components/AccessesGrid';

import { MailDomain, Role } from '../../domains';

import { ModalCreateAccess } from './ModalCreateAccess';

export const AccessesContent = ({
  mailDomain,
  currentRole,
}: {
  mailDomain: MailDomain;
  currentRole: Role;
}) => {
  const { t } = useTranslation();

  const [isModalAccessOpen, setIsModalAccessOpen] = useState(false);

  return (
    <>
      <Box
        $direction="row"
        $justify="flex-end"
        $margin={{ bottom: 'small' }}
        $align="center"
      >
        <Box $display="flex" $direction="row">
          {mailDomain?.abilities.post && (
            <Button
              aria-label={t('Add a new access in {{name}} domain', {
                name: mailDomain?.name,
              })}
              onClick={() => {
                setIsModalAccessOpen(true);
              }}
            >
              {t('Add a new access')}
            </Button>
          )}
        </Box>
      </Box>
      <AccessesGrid mailDomain={mailDomain} currentRole={currentRole} />
      {isModalAccessOpen && mailDomain && (
        <ModalCreateAccess
          mailDomain={mailDomain}
          currentRole={currentRole}
          onClose={() => setIsModalAccessOpen(false)}
        />
      )}
    </>
  );
};
