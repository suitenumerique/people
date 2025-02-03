import {
  Button,
  Modal,
  ModalSize,
  VariantType,
  useModal,
  useToastProvider,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, DropButton, IconOptions, Text } from '@/components';
import { MailDomain } from '@/features/mail-domains/domains';

import { useUpdateMailboxStatus } from '../../api/useUpdateMailboxStatus';
import { MailDomainMailbox } from '../../types';

interface PanelActionsProps {
  mailbox: MailDomainMailbox;
  mailDomain: MailDomain;
}

export const PanelActions = ({ mailDomain, mailbox }: PanelActionsProps) => {
  const { t } = useTranslation();
  const [isDropOpen, setIsDropOpen] = useState(false);
  const isEnabled = mailbox.status === 'enabled';
  const disableModal = useModal();
  const { toast } = useToastProvider();

  const { mutate: updateMailboxStatus } = useUpdateMailboxStatus();

  const handleUpdateMailboxStatus = () => {
    disableModal.close();
    updateMailboxStatus(
      {
        mailDomainSlug: mailDomain.slug,
        mailboxId: mailbox.id,
        isEnabled: !isEnabled,
      },
      {
        onError: () =>
          toast(t('Failed to update mailbox status'), VariantType.ERROR),
      },
    );
  };

  if (
    mailbox.status === 'pending' ||
    mailbox.status === 'failed' ||
    mailDomain.abilities.post === false
  ) {
    return null;
  }

  return (
    <>
      <DropButton
        button={
          <IconOptions
            isHorizontal={true}
            aria-label={t('Open the access options modal')}
          />
        }
        onOpenChange={(isOpen) => setIsDropOpen(isOpen)}
        isOpen={isDropOpen}
      >
        <Box>
          <Button
            aria-label={t('Open the modal to update the role of this access')}
            onClick={() => {
              setIsDropOpen(false);
              if (isEnabled) {
                disableModal.open();
              } else {
                handleUpdateMailboxStatus();
              }
            }}
            fullWidth
            color="primary-text"
            icon={
              <span className="material-icons" aria-hidden="true">
                {isEnabled ? 'lock' : 'lock_open'}
              </span>
            }
          >
            <Text $theme="primary">
              {isEnabled ? t('Disable mailbox') : t('Enable mailbox')}
            </Text>
          </Button>
        </Box>
      </DropButton>
      <Modal
        isOpen={disableModal.isOpen}
        onClose={disableModal.close}
        title={<Text $size="h3">{t('Disable mailbox')}</Text>}
        size={ModalSize.MEDIUM}
        rightActions={
          <Box $direction="row" $justify="flex-end" $gap="0.5rem">
            <Button color="secondary" onClick={disableModal.close}>
              {t('Cancel')}
            </Button>
            <Button color="danger" onClick={handleUpdateMailboxStatus}>
              {t('Disable')}
            </Button>
          </Box>
        }
      >
        <Text>
          {t(
            'Are you sure you want to disable this mailbox? This action results in the deletion of the calendar, address book, etc.',
          )}
        </Text>
      </Modal>
    </>
  );
};
