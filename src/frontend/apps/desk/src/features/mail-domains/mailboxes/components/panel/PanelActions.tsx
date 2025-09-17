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
import {
  ModalUpdateMailbox,
  ViewMailbox,
} from '@/features/mail-domains/mailboxes';

import {
  useResetPassword,
  useUpdateMailboxStatus,
} from '../../api/useUpdateMailboxStatus';

interface PanelActionsProps {
  mailbox: ViewMailbox;
  mailDomain: MailDomain;
}

export const PanelActions = ({ mailDomain, mailbox }: PanelActionsProps) => {
  const { t } = useTranslation();
  const [isDropOpen, setIsDropOpen] = useState(false);
  const isEnabled = mailbox.status === 'enabled';
  const disableModal = useModal();
  const updateModal = useModal();
  const { toast } = useToastProvider();

  const { mutate: updateMailboxStatus } = useUpdateMailboxStatus();
  const { mutate: resetPassword } = useResetPassword();

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

  const handleResetMailboxPassword = () => {
    resetPassword(
      {
        mailDomainSlug: mailDomain.slug,
        mailboxId: mailbox.id,
      },
      {
        onSuccess: () =>
          toast(t('Successfully reset password.'), VariantType.SUCCESS),
        onError: () => toast(t('Failed to reset password'), VariantType.ERROR),
      },
    );
  };

  if (
    mailbox.status === 'pending' ||
    mailbox.status === 'failed' ||
    (mailDomain.abilities.post === false && !mailbox.isCurrentUser)
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
            aria-label={t('Open a modal to enable or disable mailbox')}
            onClick={() => {
              setIsDropOpen(false);
              if (isEnabled) {
                disableModal.open();
              } else {
                handleUpdateMailboxStatus();
              }
            }}
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
          <Button
            aria-label={t('Open the modal to update mailbox attributes')}
            onClick={() => {
              setIsDropOpen(false);
              if (isEnabled) {
                updateModal.open();
              } else {
                handleUpdateMailboxStatus();
              }
            }}
            color="primary-text"
            disabled={!isEnabled}
            icon={
              <span className="material-icons" aria-hidden="true">
                {isEnabled ? 'settings' : 'block'}
              </span>
            }
          >
            <Text $theme={isEnabled ? 'primary' : 'greyscale'}>
              {t('Configure mailbox')}
            </Text>
          </Button>
          <Button
            aria-label={t('Reset password for this mailbox')}
            onClick={() => {
              setIsDropOpen(false);
              handleResetMailboxPassword();
            }}
            color="primary-text"
            disabled={!isEnabled}
            icon={
              <span className="material-icons" aria-hidden="true">
                {isEnabled ? 'lock_reset' : ' block'}
              </span>
            }
          >
            <Text $theme={isEnabled ? 'primary' : 'greyscale'}>
              {t('Reset password')}
            </Text>
          </Button>
        </Box>
      </DropButton>
      <ModalUpdateMailbox
        isOpen={updateModal.isOpen}
        onClose={updateModal.close}
        mailDomain={mailDomain}
        mailbox={mailbox}
      />
      <Modal
        isOpen={disableModal.isOpen}
        onClose={disableModal.close}
        hideCloseButton={true}
        title={<Text $size="h3">{t('Disable mailbox')}</Text>}
        size={ModalSize.MEDIUM}
        leftActions={
          <Button color="secondary" onClick={disableModal.close}>
            {t('Cancel')}
          </Button>
        }
        rightActions={
          <Box $direction="row" $justify="flex-end" $gap="0.5rem">
            <Button color="danger" onClick={handleUpdateMailboxStatus}>
              {t('Disable')}
            </Button>
          </Box>
        }
      >
        <Box
          $padding="md"
          aria-label={t('Content modal to delete the mailbox')}
        >
          <Text>
            {t(
              'Are you sure you want to disable this mailbox? This action results in the deletion of the calendar, address book, etc.',
            )}
          </Text>
        </Box>
      </Modal>
    </>
  );
};
