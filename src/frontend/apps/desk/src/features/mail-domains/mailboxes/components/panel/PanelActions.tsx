import {
  Button,
  Modal,
  ModalSize,
  VariantType,
  useModal,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import { DropdownMenu, useDropdownMenu } from '@gouvfr-lasuite/ui-kit';
import { useTranslation } from 'react-i18next';

import { Box, Icon, IconOptions } from '@/components';
import { MailDomain } from '@/features/mail-domains/domains';
import {
  ModalUpdateMailbox,
  ViewMailbox,
} from '@/features/mail-domains/mailboxes';

import {
  useResetPassword,
  useUpdateMailboxStatus,
} from '../../api/useUpdateMailboxStatus';

type DropdownMenuWithDisabled = React.ComponentType<
  React.ComponentProps<typeof DropdownMenu> & { isDisabled?: boolean }
>;

const DropdownMenuAny = DropdownMenu as DropdownMenuWithDisabled;

interface PanelActionsProps {
  mailbox: ViewMailbox;
  mailDomain: MailDomain;
}

export const PanelActions = ({ mailDomain, mailbox }: PanelActionsProps) => {
  const { t } = useTranslation();
  const { isOpen, setIsOpen } = useDropdownMenu();
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

  const isDisabledDropdown = false;

  return (
    <>
      <DropdownMenuAny
        options={[
          {
            label: isEnabled ? t('Disable mailbox') : t('Enable mailbox'),
            icon: (
              <Icon
                iconName={isEnabled ? 'lock' : 'lock_open'}
                $size="sm"
                aria-hidden="true"
              />
            ),
            callback: () => {
              setIsOpen(false);
              if (isEnabled) {
                disableModal.open();
              } else {
                handleUpdateMailboxStatus();
              }
            },
          },
          {
            label: t('Configure mailbox'),
            icon: (
              <Icon
                iconName={isEnabled ? 'settings' : 'block'}
                $size="sm"
                aria-hidden="true"
              />
            ),
            isDisabled: !isEnabled,
            callback: () => {
              setIsOpen(false);
              if (isEnabled) {
                updateModal.open();
              } else {
                handleUpdateMailboxStatus();
              }
            },
          },
          {
            label: t('Reset password'),
            icon: (
              <Icon
                iconName={isEnabled ? 'lock_reset' : 'block'}
                $size="sm"
                aria-hidden="true"
              />
            ),
            isDisabled: !isEnabled,
            callback: () => {
              setIsOpen(false);
              if (!isEnabled) {
                return;
              }
              handleResetMailboxPassword();
            },
          },
        ]}
        isOpen={isOpen}
        onOpenChange={setIsOpen}
        isDisabled={isDisabledDropdown}
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
          <IconOptions isHorizontal={true} />
        </button>
      </DropdownMenuAny>
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
        closeOnClickOutside={true}
        title={t('Disable mailbox')}
        size={ModalSize.MEDIUM}
        leftActions={
          <Button
            color="neutral"
            variant="secondary"
            onClick={disableModal.close}
          >
            {t('Cancel')}
          </Button>
        }
        rightActions={
          <Box $direction="row" $justify="flex-end" $gap="0.5rem">
            <Button color="error" onClick={handleUpdateMailboxStatus}>
              {t('Disable')}
            </Button>
          </Box>
        }
      >
        <div className="c__modal__content__margin">
          {t(
            'Are you sure you want to disable this mailbox? This action results in the deletion of the calendar, address book, etc.',
          )}
        </div>
      </Modal>
    </>
  );
};
