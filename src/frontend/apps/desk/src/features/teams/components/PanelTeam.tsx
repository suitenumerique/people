import React from 'react';
import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group.svg';
import { Box, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { TeamResponse } from '../api/useTeams';
import IconNone from '../assets/icon-none.svg';

interface TeamProps {
  team: TeamResponse;
}

export const PanelTeam = ({ team }: TeamProps) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  const commonProps = {
    className: 'p-t',
    width: 52,
    style: {
      borderRadius: '10px',
      flexShrink: 0,
    },
  };

  return (
    <Box as="li" $direction="row" $align="center" $gap="0.5rem">
      {team.accesses.length ? (
        <IconGroup
          aria-label={t(`Teams icon`)}
          color={colorsTokens()['primary-500']}
          {...commonProps}
          style={{
            ...commonProps.style,
            border: `1px solid ${colorsTokens()['primary-300']}`,
          }}
        />
      ) : (
        <IconNone
          aria-label={t(`Empty teams icon`)}
          color={colorsTokens()['greyscale-500']}
          {...commonProps}
          style={{
            ...commonProps.style,
            border: `1px solid ${colorsTokens()['greyscale-300']}`,
          }}
        />
      )}
      <Text $weight="bold">{team.name}</Text>
    </Box>
  );
};
