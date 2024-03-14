import { Button, Modal, ModalSize } from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createGlobalStyle } from 'styled-components';

import { Box } from '@/components';
import { Team } from '@/features/teams';

import { OptionSelect, SearchMembers } from './SearchMembers';

const GlobalStyle = createGlobalStyle`
  .c__modal {
    overflow: visible;
  }
`;

interface ModalAddMembersProps {
  onClose: () => void;
  team: Team;
}

export const ModalAddMembers = ({ onClose, team }: ModalAddMembersProps) => {
  const { t } = useTranslation();
  const [, setSelectedMembers] = useState<OptionSelect>([]);

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
        <Button color="primary" fullWidth onClick={() => {}}>
          {t('Validate')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={t('Add members to the team')}
    >
      <GlobalStyle />
      <Box className="mb-xl mt-l">
        <SearchMembers team={team} setSelectedMembers={setSelectedMembers} />
      </Box>
    </Modal>
  );
};
