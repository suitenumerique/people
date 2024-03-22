import {
  Button,
  Modal,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createGlobalStyle } from 'styled-components';

import { APIError } from '@/api';
import { Box, Text } from '@/components';
import { Team } from '@/features/teams';

import { useCreateInvitation } from '../api';
import { Invitation, Role } from '../types';

import { ChooseRole } from './ChooseRole';
import { OptionSelect, SearchMembers } from './SearchMembers';

const GlobalStyle = createGlobalStyle`
  .c__modal {
    overflow: visible;
  }
`;

interface ModalAddMembersProps {
  currentRole: Role;
  onClose: () => void;
  team: Team;
}

export const ModalAddMembers = ({
  currentRole,
  onClose,
  team,
}: ModalAddMembersProps) => {
  const { t } = useTranslation();
  const [selectedMembers, setSelectedMembers] = useState<OptionSelect>([]);
  const [selectedRole, setSelectedRole] = useState<Role>(Role.MEMBER);
  const { toast } = useToastProvider();
  const { mutateAsync: createInvitation } = useCreateInvitation();

  const handleValidate = async () => {
    const promisesMembers = selectedMembers.map((selectedMember) => {
      return createInvitation({
        email: selectedMember.value.email,
        role: selectedRole,
        teamId: team.id,
      });
    });

    const promises = await Promise.allSettled<Invitation>(promisesMembers);

    onClose();
    promises.forEach((promise) => {
      switch (promise.status) {
        case 'rejected':
          const apiError = promise.reason as APIError<string>;
          toast(
            t(`Failed to create the invitation for {{email}}`, {
              email: apiError.data,
            }),
            VariantType.ERROR,
            {
              duration: 4000,
            },
          );
          break;

        case 'fulfilled':
          toast(
            t('Invitation sent to {{email}}', {
              email: promise.value.email,
            }),
            VariantType.SUCCESS,
            {
              duration: 4000,
            },
          );
          break;
      }
    });
  };

  return (
    <Modal
      isOpen
      leftActions={
        <Button color="secondary" fullWidth onClick={onClose}>
          {t('Cancel')}
        </Button>
      }
      onClose={onClose}
      closeOnClickOutside
      hideCloseButton
      rightActions={
        <Button
          color="primary"
          fullWidth
          disabled={!selectedMembers.length}
          onClick={() => void handleValidate()}
        >
          {t('Validate')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={t('Add members to the team')}
    >
      <GlobalStyle />
      <Box className="mb-xl mt-l">
        <SearchMembers team={team} setSelectedMembers={setSelectedMembers} />
        {selectedMembers.length > 0 && (
          <Box className="mt-s">
            <Text as="h4" $textAlign="left" className="mb-t">
              {t('Choose a role')}
            </Text>
            <ChooseRole
              currentRole={currentRole}
              disabled={false}
              defaultRole={Role.MEMBER}
              setRole={setSelectedRole}
            />
          </Box>
        )}
      </Box>
    </Modal>
  );
};
