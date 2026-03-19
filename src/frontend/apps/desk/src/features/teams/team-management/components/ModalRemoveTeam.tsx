import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import { t } from 'i18next';
import { useRouter } from 'next/navigation';

import IconGroup from '@/assets/icons/icon-group.svg';
import { Box, Text, TextErrors } from '@/components';
import { Modal } from '@/components/Modal';
import { useCunninghamTheme } from '@/cunningham';

import { useRemoveTeam } from '../api/useRemoveTeam';
import IconRemove from '../assets/icon-trash.svg';
import { Team } from '../types';

interface ModalRemoveTeamProps {
  onClose: () => void;
  team: Team;
}

export const ModalRemoveTeam = ({ onClose, team }: ModalRemoveTeamProps) => {
  const { colorsTokens } = useCunninghamTheme();
  const { toast } = useToastProvider();
  const router = useRouter();

  const {
    mutate: removeTeam,
    isError,
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
    <Modal
      isOpen
      closeOnClickOutside
      hideCloseButton
      leftActions={
        <Button
          aria-label={t('Close the modal')}
          color="neutral"
          variant="secondary"
          fullWidth
          onClick={() => onClose()}
        >
          {t('Cancel')}
        </Button>
      }
      onClose={() => onClose()}
      rightActions={
        <Button
          aria-label={t('Confirm deletion')}
          color="brand"
          fullWidth
          onClick={() =>
            removeTeam({
              teamId: team.id,
            })
          }
        >
          {t('Confirm deletion')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={
        <Box $align="center" $gap="1rem">
          <IconRemove
            width={48}
            color={colorsTokens()['brand-600']}
            aria-hidden="true"
          />
          <Text $size="h3" $margin="none">
            {t('Deleting the {{teamName}} team', { teamName: team.name })}
          </Text>
        </Box>
      }
    >
      <Box
        $margin={{ bottom: 'xl' }}
        aria-label={t('Content modal to delete the team')}
      >
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
          $background={colorsTokens()['brand-150']}
          $theme="primary"
          $align="center"
          $radius="2px"
        >
          <IconGroup
            className="p-t"
            aria-hidden="true"
            color={colorsTokens()['brand-500']}
            width={58}
            style={{
              borderRadius: '8px',
              backgroundColor: '#ffffff',
              border: `1px solid ${colorsTokens()['brand-300']}`,
            }}
          />
          <Text $theme="primary" $weight="bold" $size="l">
            {team.name}
          </Text>
        </Text>
      </Box>
    </Modal>
  );
};
