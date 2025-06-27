import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { t } from 'i18next';
import { useState } from 'react';

import { Box, Text } from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';

import { useUpdateTeam } from '../api';
import { Team } from '../types';

import { InputTeamName } from './InputTeamName';

interface ModalUpdateTeamProps {
  onClose: () => void;
  team: Team;
}

export const ModalUpdateTeam = ({ onClose, team }: ModalUpdateTeamProps) => {
  const [teamName, setTeamName] = useState(team.name);
  const { toast } = useToastProvider();

  const {
    mutate: updateTeam,
    isError,
    isPending,
    error,
  } = useUpdateTeam({
    onSuccess: () => {
      toast(t('The team has been updated.'), VariantType.SUCCESS, {
        duration: 4000,
      });
      onClose();
    },
  });

  const step = 0;
  const steps = [
    {
      title: t('Update team {{teamName}}', { teamName: team.name }),
      content: (
        <Box
          $padding={{ bottom: 'md' }}
          aria-label={t('Content modal to update the team')}
        >
          <Text as="p" $margin={{ bottom: 'big' }}>
            {t('Enter the new name of the selected team')}
          </Text>
          <InputTeamName
            label={t('New name...')}
            defaultValue={team.name}
            {...{ error, isError, isPending, setTeamName }}
          />
        </Box>
      ),
      leftAction: (
        <Button
          aria-label={t('Close the modal')}
          color="secondary"
          fullWidth
          onClick={() => onClose()}
        >
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          aria-label={t('Validate the modification')}
          color="primary"
          fullWidth
          onClick={() =>
            updateTeam({
              name: teamName,
              id: team.id,
            })
          }
        >
          {t('Validate the modification')}
        </Button>
      ),
    },
  ];

  return (
    <CustomModal
      isOpen
      step={step}
      totalSteps={steps.length}
      leftActions={steps[step].leftAction}
      rightActions={steps[step].rightAction}
      size={ModalSize.MEDIUM}
      title={steps[step].title}
      onClose={onClose}
      closeOnClickOutside
      hideCloseButton
      closeOnEsc
    >
      <Box $padding={{ horizontal: 'md' }}>{steps[step].content}</Box>
    </CustomModal>
  );
};
