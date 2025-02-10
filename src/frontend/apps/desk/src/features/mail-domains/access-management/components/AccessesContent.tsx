import React, { useState } from 'react';
import { Button } from '@openfun/cunningham-react';
import { AccessesGrid } from '@/features/mail-domains/access-management/components/AccessesGrid';
import { Box } from '@/components';
import { useTranslation } from 'react-i18next';

import { MailDomain, Role } from '../../domains';
import { ModalNewAccess } from './ModalNewAccess';

export const AccessesContent = ({
  mailDomain,
  currentRole,
}: {
  mailDomain: MailDomain;
  currentRole: Role;
}) => {
  const { t } = useTranslation();

  console.log(currentRole);
  const [isModalAccessOpen, setIsModalAccessOpen] = useState(false);

  const access = {
    'role': Role.MEMBER,
  }
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
              aria-label={t('Create a new access in {{name}} domain', {
                name: mailDomain?.name,
              })}
              onClick={() => {
                setIsModalAccessOpen(true);
              }}
            >
              {t('Create a new access')}
            </Button>
          )}
        </Box>
      </Box>
       <AccessesGrid mailDomain={mailDomain} currentRole={currentRole} />
        {isModalAccessOpen &&
        mailDomain && (
        <ModalNewAccess
          mailDomain={mailDomain}
          currentRole={currentRole}
          onClose={() => setIsModalAccessOpen(false)}
        />
        )}
       </>
   )};
