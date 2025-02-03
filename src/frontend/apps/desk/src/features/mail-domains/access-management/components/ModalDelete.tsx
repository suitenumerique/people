import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { t } from 'i18next';
import { useRouter } from 'next/navigation';

import IconUser from '@/assets/icons/icon-user.svg';
import { Box, Text, TextErrors } from '@/components';
import { Modal } from '@/components/Modal';
import { useCunninghamTheme } from '@/cunningham';

import { MailDomain, Role } from '../../domains';
import { useDeleteMailDomainAccess } from '../api';
import { useWhoAmI } from '../hooks/useWhoAmI';
import { Access } from '../types';

export interface ModalDeleteProps {
  access: Access;
  currentRole: Role;
  onClose: () => void;
  mailDomain: MailDomain;
}

export const ModalDelete = ({
  access,
  onClose,
  mailDomain,
}: ModalDeleteProps) => {
  const { toast } = useToastProvider();
  const { colorsTokens } = useCunninghamTheme();
  const router = useRouter();

  const { isMyself, isLastOwner, isOtherOwner } = useWhoAmI(access);
  const isNotAllowed = isOtherOwner || isLastOwner;

  const {
    mutate: removeMailDomainAccess,
    error: errorDeletion,
    isError: isErrorUpdate,
  } = useDeleteMailDomainAccess({
    onSuccess: () => {
      toast(
        t('The access has been removed from the domain'),
        VariantType.SUCCESS,
        {
          duration: 4000,
        },
      );

      // If we remove ourselves, we redirect to the home page
      // because we are no longer part of the domain
      if (isMyself) {
        router.push('/');
      } else {
        onClose();
      }
    },
  });

  return (
    <Modal
      isOpen
      closeOnClickOutside
      hideCloseButton
      leftActions={
        <Button color="secondary" fullWidth onClick={() => onClose()}>
          {t('Cancel')}
        </Button>
      }
      onClose={onClose}
      rightActions={
        <Button
          color="primary"
          fullWidth
          onClick={() => {
            removeMailDomainAccess({
              slug: mailDomain.slug,
              accessId: access.id,
            });
          }}
          disabled={isNotAllowed}
        >
          {t('Remove from the domain')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={
        <Box $align="left" $gap="1rem">
          <Text $margin="none">{t('Remove this access from the domain')}</Text>
        </Box>
      }
    >
      <Box $padding="md" aria-label={t('Radio buttons to update the roles')}>
        <Text>
          {t(
            'Are you sure you want to remove this access from the {{domain}} domain?',
            { domain: mailDomain.name },
          )}
        </Text>

        {isErrorUpdate && (
          <TextErrors
            $margin={{ bottom: 'small' }}
            causes={errorDeletion.cause}
          />
        )}

        {(isLastOwner || isOtherOwner) && (
          <Text
            $theme="warning"
            $direction="row"
            $align="center"
            $gap="0.5rem"
            $margin="tiny"
            $justify="center"
          >
            <span className="material-icons">warning</span>
            {isLastOwner &&
              t(
                'You are the last owner, you cannot be removed from your domain.',
              )}
            {isOtherOwner && t('You cannot remove other owner.')}
          </Text>
        )}

        <Text
          as="p"
          $padding="big"
          $direction="row"
          $gap="0.5rem"
          $background={colorsTokens()['primary-150']}
          $theme="primary"
        >
          <IconUser width={20} height={20} aria-hidden="true" />
          <Text>{access.user.name}</Text>
        </Text>
      </Box>
    </Modal>
  );
};
