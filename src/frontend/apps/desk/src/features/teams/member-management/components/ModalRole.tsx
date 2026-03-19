import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text, TextErrors } from '@/components';
import { Modal } from '@/components/Modal';
import { Role } from '@/features/teams/team-management';

import { useUpdateTeamAccess } from '../api/useUpdateTeamAccess';
import { useWhoAmI } from '../hooks/useWhoAmI';
import { Access } from '../types';

import { ChooseRole } from './ChooseRole';

interface ModalRoleProps {
  access: Access;
  currentRole: Role;
  onClose: () => void;
  teamId: string;
}

export const ModalRole = ({
  access,
  currentRole,
  onClose,
  teamId,
}: ModalRoleProps) => {
  const { t } = useTranslation();
  const [localRole, setLocalRole] = useState(access.role);
  const { toast } = useToastProvider();
  const {
    mutate: updateTeamAccess,
    error: errorUpdate,
    isError: isErrorUpdate,
    isPending,
  } = useUpdateTeamAccess({
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
          color="neutral"
          variant="secondary"
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
          color="brand"
          fullWidth
          onClick={() => {
            updateTeamAccess({
              role: localRole,
              teamId,
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
                'You are the sole owner of this group. Make another member the group owner, before you can change your own role.',
              )}
            {isOtherOwner && t('You cannot update the role of other owner.')}
          </Text>
        )}

        <ChooseRole
          defaultRole={access.role}
          currentRole={currentRole}
          disabled={isNotAllowed}
          setRole={setLocalRole}
        />
      </Box>
    </Modal>
  );
};
