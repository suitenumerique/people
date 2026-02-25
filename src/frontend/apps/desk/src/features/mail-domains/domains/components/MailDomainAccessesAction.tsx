import { DropdownMenu, useDropdownMenu } from '@gouvfr-lasuite/ui-kit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Icon, IconOptions } from '@/components';
import { ModalDomainAccessesManagement } from '@/features/mail-domains/access-management/components/ModalDomainAccessesManagement';
import { MailDomain, Role } from '@/features/mail-domains/domains';

type MailDomainAccessesActionProps = {
  mailDomain: MailDomain;
  currentRole: Role;
  onConfigureDomain?: () => void;
};

export const MailDomainAccessesAction = ({
  mailDomain,
  currentRole,
  onConfigureDomain,
}: MailDomainAccessesActionProps) => {
  const { t } = useTranslation();
  const { isOpen, setIsOpen } = useDropdownMenu();
  const [isModalAccessOpen, setIsModalAccessOpen] = useState(false);

  const openAccessManagement = () => {
    setIsOpen(false);
    setIsModalAccessOpen(true);
  };

  const openConfigureDomain = () => {
    setIsOpen(false);
    onConfigureDomain?.();
  };

  const options = [
    ...(mailDomain?.abilities.post
      ? [
          {
            label: t('Access management'),
            icon: <Icon iconName="manage_accounts" $size="sm" />,
            callback: openAccessManagement,
          },
        ]
      : []),
    ...(onConfigureDomain
      ? [
          {
            label: t('Configure domain'),
            icon: <Icon iconName="settings" $size="sm" />,
            callback: openConfigureDomain,
          },
        ]
      : []),
  ];

  if (!mailDomain?.abilities.post && !onConfigureDomain) {
    return null;
  }

  return (
    <>
      <Box $direction="row" $justify="flex-end" $align="center">
        <DropdownMenu
          options={options}
          isOpen={isOpen}
          onOpenChange={setIsOpen}
        >
          <button
            type="button"
            aria-label={t('Open domain options menu')}
            onClick={() => setIsOpen(!isOpen)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <IconOptions isHorizontal={true} />
          </button>
        </DropdownMenu>
      </Box>
      {isModalAccessOpen && mailDomain && (
        <ModalDomainAccessesManagement
          mailDomain={mailDomain}
          currentRole={currentRole}
          onClose={() => setIsModalAccessOpen(false)}
        />
      )}
    </>
  );
};
