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
import { CustomModal } from '@/components/modal/CustomModal';
import { useCunninghamTheme } from '@/cunningham';
import { Role, Team } from '@/features/teams/team-management';

import { useDeleteTeamAccess } from '../api/useDeleteTeamAccess';
import { useWhoAmI } from '../hooks/useWhoAmI';
import { Access } from '../types';

interface ModalDeleteProps {
  access: Access;
  currentRole: Role;
  onClose: () => void;
  team: Team;
}

export const ModalDelete = ({ access, onClose, team }: ModalDeleteProps) => {
  const { toast } = useToastProvider();
  const { colorsTokens } = useCunninghamTheme();
  const router = useRouter();

  const { isMyself, isLastOwner, isOtherOwner } = useWhoAmI(access);
  const isNotAllowed = isOtherOwner || isLastOwner;

  const {
    mutate: removeTeamAccess,
    error: errorUpdate,
    isError: isErrorUpdate,
  } = useDeleteTeamAccess({
    onSuccess: () => {
      toast(
        t('The member has been removed from the team'),
        VariantType.SUCCESS,
        {
          duration: 4000,
        },
      );

      // If we remove ourselves, we redirect to the home page
      // because we are no longer part of the team
      if (isMyself) {
        router.push('/');
      } else {
        onClose();
      }
    },
  });

  const step = 0;
  const steps = [
    {
      title: t('Remove this member from the group'),
      content: (
        <Box
          $padding={{ horizontal: 'md', bottom: 'md' }}
          aria-label={t('Radio buttons to update the roles')}
        >
          <Text>
            {t(
              'Are you sure you want to remove this member from the {{team}} group?',
              { team: team.name },
            )}
          </Text>

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
              $gap="1rem"
              $margin="md"
              $justify="center"
            >
              <span className="material-icons">warning</span>
              {isLastOwner &&
                t(
                  'You are the last owner, you cannot be removed from your team.',
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
      ),
      leftAction: (
        <Button color="secondary" fullWidth onClick={() => onClose()}>
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          color="primary"
          fullWidth
          onClick={() => {
            removeTeamAccess({
              teamId: team.id,
              accessId: access.id,
            });
          }}
          disabled={isNotAllowed}
        >
          {t('Remove from the group')}
        </Button>
      ),
    },
  ];

  return (
    <CustomModal
      isOpen
      closeOnClickOutside
      hideCloseButton
      leftActions={steps[step].leftAction}
      rightActions={steps[step].rightAction}
      onClose={onClose}
      size={ModalSize.MEDIUM}
      title={steps[step].title}
      step={step}
      totalSteps={steps.length}
      closeOnEsc
    >
      {steps[step].content}
    </CustomModal>
  );
};
