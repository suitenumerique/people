import {
  Button,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import { DropdownMenu, useDropdownMenu } from '@gouvfr-lasuite/ui-kit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Icon, IconOptions } from '@/components';
import { useUpdateMailDomainAccess } from '@/features/mail-domains/access-management';

import { MailDomain, Role } from '../../domains/types';
import { Access } from '../types';

import { ModalDelete } from './ModalDelete';

interface AccessActionProps {
  access: Access;
  currentRole: Role;
  mailDomain: MailDomain;
}

export const AccessAction = ({
  access,
  currentRole,
  mailDomain,
}: AccessActionProps) => {
  const { t } = useTranslation();
  const { isOpen, setIsOpen } = useDropdownMenu();
  const [isModalDeleteOpen, setIsModalDeleteOpen] = useState(false);
  const { toast } = useToastProvider();

  const { mutate: updateMailDomainAccess } = useUpdateMailDomainAccess({
    onSuccess: () => {
      toast(t('The role has been updated'), VariantType.SUCCESS, {
        duration: 4000,
      });
    },
  });

  if (currentRole === Role.VIEWER) {
    return null;
  }

  const canUpdateRole =
    (mailDomain.abilities.put || mailDomain.abilities.patch) &&
    access.can_set_role_to &&
    access.can_set_role_to.length > 0;
  const canDelete = mailDomain.abilities.delete;

  const localizedRoles = {
    [Role.ADMIN]: t('Administrator'),
    [Role.VIEWER]: t('Viewer'),
    [Role.OWNER]: t('Owner'),
  };

  const menuOptions = [
    ...(canUpdateRole
      ? (access.can_set_role_to ?? []).map((role) => ({
          label: localizedRoles[role],
          callback: () => {
            setIsOpen(false);
            updateMailDomainAccess({
              slug: mailDomain.slug,
              accessId: access.id,
              role,
            });
          },
        }))
      : []),
    ...(canDelete
      ? [
          ...(canUpdateRole ? [{ type: 'separator' as const }] : []),
          {
            label: t('Remove from domain'),
            callback: () => {
              setIsOpen(false);
              setIsModalDeleteOpen(true);
            },
            variant: 'danger' as const,
          },
        ]
      : []),
  ];

  const roleLabel = localizedRoles[access.role];

  if (!canUpdateRole && !canDelete) {
    return (
      <Button variant="tertiary" color="neutral" size="small" disabled>
        {roleLabel}
      </Button>
    );
  }

  if (canUpdateRole) {
    return (
      <>
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
            >
              {roleLabel}
            </Button>
          </DropdownMenu>
        </Box>

        {isModalDeleteOpen && canDelete && (
          <ModalDelete
            access={access}
            currentRole={currentRole}
            onClose={() => setIsModalDeleteOpen(false)}
            mailDomain={mailDomain}
          />
        )}
      </>
    );
  }

  return (
    <>
      <Box $display="inline-flex" $direction="row" $align="center" $gap="xs">
        <Button variant="tertiary" color="neutral" size="small" disabled>
          {roleLabel}
        </Button>
        <DropdownMenu
          options={menuOptions}
          isOpen={isOpen}
          onOpenChange={setIsOpen}
        >
          <button
            type="button"
            aria-label={t('Open the access options modal')}
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
            <IconOptions />
          </button>
        </DropdownMenu>
      </Box>

      {isModalDeleteOpen && canDelete && (
        <ModalDelete
          access={access}
          currentRole={currentRole}
          onClose={() => setIsModalDeleteOpen(false)}
          mailDomain={mailDomain}
        />
      )}
    </>
  );
};
