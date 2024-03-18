import { Button, Modal, ModalSize } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';

interface ModalAddMembersProps {
  onClose: () => void;
}

export const ModalAddMembers = ({ onClose }: ModalAddMembersProps) => {
  const { t } = useTranslation();

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
    ></Modal>
  );
};
