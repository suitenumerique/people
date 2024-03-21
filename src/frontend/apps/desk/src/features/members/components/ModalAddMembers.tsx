import { Button, Modal, ModalSize } from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createGlobalStyle } from 'styled-components';

import { Box, Text } from '@/components';
import { Team } from '@/features/teams';

import { Role } from '../types';

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
  const [, setSelectedRole] = useState<Role>(Role.MEMBER);

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
          onClick={() => {}}
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
