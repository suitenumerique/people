import {
  Button,
  Modal,
  ModalSize,
  Radio,
  RadioGroup,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { t } from 'i18next';
import { useState } from 'react';

import { Box, Text, TextErrors } from '@/components';
import { useAuthStore } from '@/features/auth';
import { Access, Role, useUpdateTeamAccess } from '@/features/teams/api/';

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
  const [localRole, setLocalRole] = useState(access.role);
  const { userData } = useAuthStore();
  const { toast } = useToastProvider();
  const {
    mutate: updateTeamAccess,
    error: errorUpdate,
    isError: isErrorUpdate,
  } = useUpdateTeamAccess({
    onSuccess: () => {
      toast(t('The role has been updated'), VariantType.SUCCESS, {
        duration: 4000,
      });
      onClose();
    },
  });

  const rolesAllowed = access.abilities.set_role_to;
  const isLastOwner =
    !rolesAllowed.length &&
    access.role === Role.OWNER &&
    userData?.id === access.user.id;

  const isOtherOwner =
    access.role === Role.OWNER &&
    userData?.id &&
    userData.id !== access.user.id;

  const isNotAllowed = isOtherOwner || isLastOwner;

  return (
    <Modal
      isOpen
      leftActions={
        <Button color="secondary" fullWidth onClick={() => onClose()}>
          {t('Cancel')}
        </Button>
      }
      onClose={() => onClose()}
      rightActions={
        <Button
          color="primary"
          fullWidth
          onClick={() => {
            updateTeamAccess({
              role: localRole,
              teamId,
              accessId: access.id,
            });
          }}
          disabled={isNotAllowed}
        >
          {t('Validate')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={t('Update the role')}
    >
      <Box aria-label={t('Radio buttons to update the roles')}>
        {isErrorUpdate && (
          <TextErrors className="mb-s" causes={errorUpdate.cause} />
        )}

        {(isLastOwner || isOtherOwner) && (
          <Text
            $theme="warning"
            $direction="row"
            $align="center"
            $gap="0.5rem"
            className="mb-t"
            $justify="center"
          >
            <span className="material-icons">warning</span>
            {isLastOwner &&
              t('You are the last owner, you cannot change your role.')}
            {isOtherOwner && t('You cannot update the role of other owner.')}
          </Text>
        )}

        <RadioGroup>
          <Radio
            label={t('Admin')}
            value={Role.ADMIN}
            name="role"
            onChange={(evt) => setLocalRole(evt.target.value as Role)}
            defaultChecked={access.role === Role.ADMIN}
            disabled={isNotAllowed}
          />
          <Radio
            label={t('Member')}
            value={Role.MEMBER}
            name="role"
            onChange={(evt) => setLocalRole(evt.target.value as Role)}
            defaultChecked={access.role === Role.MEMBER}
            disabled={isNotAllowed}
          />
          <Radio
            label={t('Owner')}
            value={Role.OWNER}
            name="role"
            onChange={(evt) => setLocalRole(evt.target.value as Role)}
            defaultChecked={access.role === Role.OWNER}
            disabled={isNotAllowed || currentRole !== Role.OWNER}
          />
        </RadioGroup>
      </Box>
    </Modal>
  );
};
