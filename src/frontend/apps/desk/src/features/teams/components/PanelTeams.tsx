import { Loader } from '@openfun/cunningham-react';
import React, { useMemo, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { InfiniteScroll } from '@/components/InfiniteScroll';

import { Team } from '../api/types';
import { useTeams } from '../api/useTeams';
import { useTeamStore } from '../store/useTeamsStore';

import { PanelTeam } from './PanelTeam';

interface PanelTeamsStateProps {
  isLoading: boolean;
  isError: boolean;
  teams?: Team[];
}

const PanelTeamsState = ({
  isLoading,
  isError,
  teams,
}: PanelTeamsStateProps) => {
  const { t } = useTranslation();

  if (isError) {
    return (
      <Box $justify="center" className="mb-b">
        <Text $theme="danger" $align="center" $textAlign="center">
          {t('Something bad happens, please refresh the page.')}
        </Text>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box $align="center" className="m-l">
        <Loader />
      </Box>
    );
  }

  if (!teams?.length) {
    return (
      <Box $justify="center" className="m-s">
        <Text as="p" className="mb-0 mt-0" $theme="greyscale" $variation="500">
          {t('0 group to display.')}
        </Text>
        <Text as="p" $theme="greyscale" $variation="500">
          {t(
            'Create your first team by clicking on the "Create a new team" button.',
          )}
        </Text>
      </Box>
    );
  }

  return teams.map((team) => <PanelTeam team={team} key={team.id} />);
};

export const PanelTeams = () => {
  const ordering = useTeamStore((state) => state.ordering);
  const {
    data,
    isError,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useTeams({
    ordering,
  });
  const containerRef = useRef<HTMLDivElement>(null);
  const teams = useMemo(() => {
    return data?.pages.reduce((acc, page) => {
      return acc.concat(page.results);
    }, [] as Team[]);
  }, [data?.pages]);

  return (
    <Box $css="overflow: auto;" ref={containerRef}>
      <InfiniteScroll
        hasMore={hasNextPage}
        isLoading={isFetchingNextPage}
        next={() => {
          void fetchNextPage();
        }}
        scrollContainer={containerRef.current}
        as="ul"
        className="p-0 mt-0"
        role="listbox"
      >
        <PanelTeamsState
          isLoading={isLoading}
          isError={isError}
          teams={teams}
        />
      </InfiniteScroll>
    </Box>
  );
};
