import { DateTime, DateTimeFormatOptions } from 'luxon';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group2.svg';
import { Box, Card, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { Role, Team } from '../types';

import { ModalUpdateTeam } from './ModalUpdateTeam';
import { TeamActions } from './TeamActions';

const format: DateTimeFormatOptions = {
  month: '2-digit',
  day: '2-digit',
  year: 'numeric',
};

interface TeamInfoProps {
  team: Team;
  currentRole: Role;
}

export const TeamInfo = ({ team, currentRole }: TeamInfoProps) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();
  const { i18n } = useTranslation();
  const [isModalUpdateOpen, setIsModalUpdateOpen] = useState(false);

  const created_at = DateTime.fromISO(team.created_at)
    .setLocale(i18n.language)
    .toLocaleString(format);

  const updated_at = DateTime.fromISO(team.updated_at)
    .setLocale(i18n.language)
    .toLocaleString(format);

  return (
    <>
      <Card $margin="big" $padding={{ bottom: 'none' }}>
        <Box $css="align-self: flex-end;" $margin="tiny" $position="absolute">
          <TeamActions currentRole={currentRole} team={team} />
        </Box>
        <Box $margin="big" $direction="row" $align="center" $gap="1.5rem">
          <IconGroup
            aria-hidden="true"
            width={44}
            color={colorsTokens()['primary-text']}
            style={{
              flexShrink: 0,
              alignSelf: 'start',
            }}
          />
          <Box>
            <Text
              as="h3"
              $weight="bold"
              $size="1.25rem"
              $margin={{ top: 'none' }}
            >
              {team.name}
            </Text>
            <Text $size="m">{t('Group details')}</Text>
          </Box>
        </Box>
        <Box
          $padding={{ all: 'small', left: '1.5rem' }}
          $gap="3rem"
          $direction="row"
          $justify="start"
          $css={`
            border-top: 1px solid ${colorsTokens()['greyscale-200']};
          `}
        >
          <Text $size="s" as="p">
            {t('{{count}} member', { count: team.accesses.length })}
          </Text>
          <Text $size="s" $display="inline" as="p">
            {t('Created at')}&nbsp;
            <Text $weight="bold" $display="inline">
              {created_at}
            </Text>
          </Text>
          <Text $size="s" $display="inline" as="p">
            {t('Last update at')}&nbsp;
            <Text $weight="bold" $display="inline">
              {updated_at}
            </Text>
          </Text>
        </Box>
      </Card>
      {isModalUpdateOpen && (
        <ModalUpdateTeam
          onClose={() => setIsModalUpdateOpen(false)}
          team={team}
        />
      )}
    </>
  );
};
