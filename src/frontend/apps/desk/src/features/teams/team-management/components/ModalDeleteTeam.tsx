import {
  Button,
  Loader,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { t } from 'i18next';
import { useRouter } from 'next/navigation';

import IconGroup from '@/assets/icons/icon-group.svg';
import { Box, Text, TextErrors } from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';
import { useCunninghamTheme } from '@/cunningham';

import { useRemoveTeam } from '../api/useRemoveTeam';
import { Team } from '../types';

interface ModalDeleteTeamProps {
  onClose: () => void;
  team: Team;
}

export const ModalDeleteTeam = ({ onClose, team }: ModalDeleteTeamProps) => {
  const { colorsTokens } = useCunninghamTheme();
  const { toast } = useToastProvider();
  const router = useRouter();

  const {
    mutate: removeTeam,
    isError,
    isPending,
    error,
  } = useRemoveTeam({
    onSuccess: () => {
      toast(t('The team has been removed.'), VariantType.SUCCESS, {
        duration: 4000,
      });
      router.push('/');
    },
  });

  return (
    <CustomModal
      isOpen
      hideCloseButton
      closeOnClickOutside
      closeOnEsc
      onClose={onClose}
      leftActions={
        <Button
          aria-label={t('Close the modal')}
          color="secondary"
          fullWidth
          onClick={onClose}
        >
          {t('Cancel')}
        </Button>
      }
      rightActions={
        <Button
          aria-label={t('Confirm deletion')}
          color="primary"
          fullWidth
          onClick={() =>
            removeTeam({
              teamId: team.id,
            })
          }
          disabled={isPending}
        >
          {t('Confirm deletion')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={t('Deleting the {{teamName}} team', { teamName: team.name })}
    >
      <Box $padding="md">
        <Box aria-label={t('Content modal to delete the team')}>
          <Text as="p" $margin={{ bottom: 'big' }}>
            {t('Are you sure you want to delete {{teamName}} team?', {
              teamName: team.name,
            })}
          </Text>

          {isError && (
            <TextErrors $margin={{ bottom: 'small' }} causes={error.cause} />
          )}

          <Text
            as="p"
            $padding="small"
            $direction="row"
            $gap="0.5rem"
            $background={colorsTokens()['primary-150']}
            $theme="primary"
            $align="center"
            $radius="2px"
          >
            <IconGroup
              className="p-t"
              aria-hidden="true"
              color={colorsTokens()['primary-500']}
              width={58}
              style={{
                borderRadius: '8px',
                backgroundColor: '#ffffff',
                border: `1px solid ${colorsTokens()['primary-300']}`,
              }}
            />
            <Text $theme="primary" $weight="bold" $size="l">
              {team.name}
            </Text>
          </Text>
        </Box>
        {isPending && (
          <Box $align="center">
            <Loader />
          </Box>
        )}
      </Box>
    </CustomModal>
  );
};
