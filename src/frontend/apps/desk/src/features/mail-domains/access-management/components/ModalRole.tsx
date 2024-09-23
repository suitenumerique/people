import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text, TextErrors } from '@/components';
import { Modal } from '@/components/Modal';
import { useUpdateMailDomainAccess } from '@/features/mail-domains/access-management';

import { Role } from '../../domains';
import { useWhoAmI } from '../hooks/useWhoAmI';
import { Access } from '../types';

import { ChooseRole } from './ChooseRole';

interface ModalRoleProps {
  access: Access;
  currentRole: Role;
  onClose: () => void;
  slug: string;
}

export const ModalRole = ({
  access,
  currentRole,
  onClose,
  slug,
}: ModalRoleProps) => {
  const { t } = useTranslation();
  const [localRole, setLocalRole] = useState(access.role);
  const { toast } = useToastProvider();
  const {
    mutate: updateMailDomainAccess,
    error: errorUpdate,
    isError: isErrorUpdate,
    isPending,
  } = useUpdateMailDomainAccess({
    onSuccess: () => {
      toast(t('The role has been updated'), VariantType.SUCCESS, {
        duration: 4000,
      });
      onClose();
    },
  });
  const { isLastOwner, isOtherOwner } = useWhoAmI(access);

  const isNotAllowed = isOtherOwner || isLastOwner;

  return (
    <Modal
      isOpen
      leftActions={
        <Button
          color="secondary"
          fullWidth
          onClick={() => onClose()}
          disabled={isPending}
        >
          {t('Cancel')}
        </Button>
      }
      onClose={() => onClose()}
      closeOnClickOutside
      hideCloseButton
      rightActions={
        <Button
          color="primary"
          fullWidth
          onClick={() => {
            updateMailDomainAccess({
              role: localRole,
              slug,
              accessId: access.id,
            });
          }}
          disabled={isNotAllowed || isPending}
        >
          {t('Validate')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={t('Update the role')}
    >
      <Box aria-label={t('Radio buttons to update the roles')}>
        {isErrorUpdate && (
          <TextErrors
            $margin={{ bottom: 'small' }}
            causes={errorUpdate.cause}
          />
        )}

        {(isLastOwner || isOtherOwner) && (
          <Text
            $theme="warning"
            $direction="row"
            $align="center"
            $gap="0.5rem"
            $margin={{ bottom: 'tiny' }}
            $justify="center"
          >
            <span className="material-icons">warning</span>
            {isLastOwner &&
              t(
                'You are the sole owner of this domain. Make another member the domain owner, before you can change your own role.',
              )}
            {isOtherOwner && t('You cannot update the role of other owner.')}
          </Text>
        )}

        <ChooseRole
          availableRoles={access.can_set_role_to}
          currentRole={currentRole}
          disabled={isNotAllowed}
          setRole={setLocalRole}
        />
      </Box>
    </Modal>
  );
};
