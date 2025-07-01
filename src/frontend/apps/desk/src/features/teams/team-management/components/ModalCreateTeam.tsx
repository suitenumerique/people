import { Button, ModalSize } from '@openfun/cunningham-react';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box } from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';
import { useCreateTeam } from '@/features/teams/team-management/api';
import { InputTeamName } from '@/features/teams/team-management/components/InputTeamName';

export const ModalCreateTeam = ({ closeModal }: { closeModal: () => void }) => {
  const { t } = useTranslation();
  const router = useRouter();
  const step = 0;

  const {
    mutate: createTeam,
    isError,
    isPending,
    error,
  } = useCreateTeam({
    onSuccess: (team) => {
      router.push(`/teams/${team.id}`);
    },
  });

  const [teamName, setTeamName] = useState('');

  const steps = [
    {
      title: t('Create a new team'),
      content: (
        <InputTeamName
          label={t('Team name')}
          {...{ error, isError, isPending, setTeamName }}
        />
      ),
      leftAction: (
        <Button color="secondary" onClick={closeModal}>
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          onClick={() => createTeam(teamName)}
          disabled={!teamName || isPending}
        >
          {t('Create the team')}
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
      hideCloseButton
      closeOnClickOutside
      onClose={closeModal}
      closeOnEsc
      rightActions={steps[step].rightAction}
      size={ModalSize.MEDIUM}
      title={steps[step].title}
    >
      <Box $padding="md">{steps[step].content}</Box>
    </CustomModal>
  );
};
