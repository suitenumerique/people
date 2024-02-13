import React from 'react';
import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group2.svg';
import { Box, Card, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { TeamResponse } from '../api/types';

interface TeamInfoProps {
  team: TeamResponse;
}

export const TeamInfo = ({ team }: TeamInfoProps) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Card className="m-b" style={{ paddingBottom: 0 }}>
      <Box className="m-b" $direction="row" $align="center" $gap="1.5rem">
        <IconGroup
          width={44}
          color={colorsTokens()['primary-text']}
          aria-label={t('icon group')}
          style={{
            flexShrink: 0,
            alignSelf: 'start',
          }}
        />
        <Box>
          <Text as="h3" $weight="bold" $size="1.25rem" className="mt-0">
            {t('Members of “{{teamName}}“', {
              teamName: team.name,
            })}
          </Text>
          <Text $size="m">
            {t('Add people to the “{{teamName}}“ group.', {
              teamName: team.name,
            })}
          </Text>
        </Box>
      </Box>
      <Box
        className="p-s"
        $gap="1rem"
        $direction="row"
        $justify="space-evenly"
        $css={`border-top: 1px solid ${colorsTokens()['card-border']};`}
      >
        <Text $size="s">
          {t('{{count}} member', { count: team.accesses.length })}
        </Text>
        <Text $size="s" $direction="row">
          {t('Created at')}&nbsp;
          <Text $weight="bold">06/02/2024</Text>
        </Text>
        <Text $size="s" $direction="row">
          {t('Last update at')}&nbsp;
          <Text $weight="bold">07/02/2024</Text>
        </Text>
      </Box>
    </Card>
  );
};
