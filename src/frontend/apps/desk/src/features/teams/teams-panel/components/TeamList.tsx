import { Loader } from '@gouvfr-lasuite/cunningham-react';
import React, { useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { useAuthStore } from '@/core/auth';
import { Team, useTeams } from '@/features/teams/team-management';

import { useTeamStore } from '../store';

import { TeamItem } from './TeamItem';

interface PanelTeamsStateProps {
  isLoading: boolean;
  isError: boolean;
  teams?: Team[];
}

const TeamListState = ({ isLoading, isError, teams }: PanelTeamsStateProps) => {
  const { t } = useTranslation();
  const { userData } = useAuthStore();

  const can_create = userData?.abilities?.teams.can_create ?? false;

  if (isError) {
    return (
      <Box $justify="center" $margin={{ bottom: 'big' }}>
        <Text $theme="danger" $align="center" $textAlign="center">
          {t('Something bad happens, please refresh the page.')}
        </Text>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box $align="center" $margin="large">
        <Loader />
      </Box>
    );
  }

  if (!teams?.length) {
    return (
      <Box $justify="center" $margin="small">
        <Text as="p" $margin={{ vertical: 'none' }}>
          {t('0 group to display.')}
        </Text>
        {can_create && (
          <Text as="p">
            {t(
              'Create your first team by clicking on the "Create a new team" button.',
            )}
          </Text>
        )}
      </Box>
    );
  }

  return teams.map((team) => <TeamItem team={team} key={team.id} />);
};

export const TeamList = () => {
  const ordering = useTeamStore((state) => state.ordering);
  const { data, isError, isLoading } = useTeams({
    ordering,
  });
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <Box $css="overflow-y: auto; overflow-x: hidden;" ref={containerRef}>
      <TeamListState isLoading={isLoading} isError={isError} teams={data} />
    </Box>
  );
};
