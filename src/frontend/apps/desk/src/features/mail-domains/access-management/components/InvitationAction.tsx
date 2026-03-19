import {
  Button,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import { DropdownMenu, useDropdownMenu } from '@gouvfr-lasuite/ui-kit';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Icon } from '@/components';

import { MailDomain, Role } from '../../domains/types';
import { useDeleteMailDomainInvitation } from '../api';
import { Access } from '../types';

interface InvitationActionProps {
  access: Access;
  currentRole: Role;
  mailDomain: MailDomain;
}

export const InvitationAction = ({
  access,
  currentRole,
  mailDomain,
}: InvitationActionProps) => {
  const { t } = useTranslation();
  const { isOpen, setIsOpen } = useDropdownMenu();
  const { toast } = useToastProvider();

  const { mutate: deleteMailDomainInvitation } = useDeleteMailDomainInvitation({
    onSuccess: () => {
      toast(t('The invitation has been deleted'), VariantType.SUCCESS, {
        duration: 4000,
      });
    },
  });

  if (currentRole === Role.VIEWER) {
    return null;
  }

  const canDelete = currentRole === Role.OWNER || currentRole === Role.ADMIN;

  const localizedRoles = {
    [Role.ADMIN]: t('Administrator'),
    [Role.VIEWER]: t('Viewer'),
    [Role.OWNER]: t('Owner'),
  };

  const roleLabel = localizedRoles[access.role];

  const menuOptions = canDelete
    ? [
        {
          label: t('Delete invitation'),
          callback: () => {
            setIsOpen(false);
            deleteMailDomainInvitation({
              slug: mailDomain.slug,
              invitationId: access.id,
            });
          },
          variant: 'danger' as const,
        },
      ]
    : [];

  if (!canDelete) {
    return (
      <Button variant="tertiary" color="neutral" size="small" disabled>
        {roleLabel}
      </Button>
    );
  }

  return (
    <Box $display="inline-flex">
      <DropdownMenu
        options={menuOptions}
        isOpen={isOpen}
        onOpenChange={setIsOpen}
      >
        <Button
          variant="tertiary"
          color="brand"
          size="small"
          onClick={() => setIsOpen(!isOpen)}
          icon={<Icon iconName="expand_more" $size="sm" $color="brand" />}
          iconPosition="right"
          aria-label={t('Open the invitation options modal')}
        >
          {roleLabel}
        </Button>
      </DropdownMenu>
    </Box>
  );
};
