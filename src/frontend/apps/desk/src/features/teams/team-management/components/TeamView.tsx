import { Button } from '@openfun/cunningham-react';
import { DateTime, DateTimeFormatOptions } from 'luxon';
import { useRouter } from 'next/router';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, IconOptions, Text } from '@/components';
import { DropButton } from '@/components/DropButton';
import { useCunninghamTheme } from '@/cunningham';

import { Role, Team } from '../types';

import { ModalDeleteTeam } from './ModalDeleteTeam';
import { ModalUpdateTeam } from './ModalUpdateTeam';

const format: DateTimeFormatOptions = {
  month: '2-digit',
  day: '2-digit',
  year: 'numeric',
};

interface TeamViewProps {
  team: Team;
  currentRole: Role;
}

export const TeamView = ({ team, currentRole }: TeamViewProps) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();
  const { i18n } = useTranslation();
  const [isModalUpdateOpen, setIsModalUpdateOpen] = useState(false);
  const [isModalDeleteOpen, setIsModalDeleteOpen] = useState(false);
  const [isDropOpen, setIsDropOpen] = useState(false);
  const router = useRouter();

  if (
    !team ||
    typeof team !== 'object' ||
    !('created_at' in team) ||
    !('updated_at' in team) ||
    !('name' in team)
  ) {
    return null;
  }

  const created_at = DateTime.fromISO(String(team.created_at))
    .setLocale(i18n.language)
    .toLocaleString(format);

  const updated_at = DateTime.fromISO(String(team.updated_at))
    .setLocale(i18n.language)
    .toLocaleString(format);

  return (
    <>
      <Box aria-label="Team panel" className="container">
        <Box
          $padding={{ horizontal: 'md' }}
          $background="white"
          $justify="space-between"
          $gap="8px"
          $align="center"
          $radius="4px"
          $direction="row"
          $css={`
            border: 1px solid ${colorsTokens()['greyscale-200']};
          `}
        >
          <Box $direction="row" $align="center" $gap="8px">
            <Button
              onClick={() => {
                void router.push('/teams/');
              }}
              icon={<span className="material-icons">arrow_back</span>}
              iconPosition="left"
              color="secondary"
              style={{
                fontWeight: '500',
              }}
            >
              {t('Teams')}
            </Button>
            <Box>
              <Text
                as="h3"
                $padding={{ left: '1.5rem' }}
                $size="h5"
                $weight="bold"
                $theme="greyscale"
              >
                {String(team.name)}
              </Text>
            </Box>
          </Box>
          <Box $align="center">
            {currentRole !== Role.MEMBER && (
              <DropButton
                button={<IconOptions aria-label={t('Open the team options')} />}
                onOpenChange={(open: boolean) => setIsDropOpen(open)}
                isOpen={isDropOpen}
              >
                <Box>
                  <Button
                    onClick={() => {
                      setIsModalUpdateOpen(true);
                      setIsDropOpen(false);
                    }}
                    color="primary-text"
                    icon={
                      <span className="material-icons" aria-hidden="true">
                        edit
                      </span>
                    }
                  >
                    <Text $theme="primary">{t('Update the team')}</Text>
                  </Button>
                  {currentRole === Role.OWNER && (
                    <Button
                      onClick={() => {
                        setIsModalDeleteOpen(true);
                        setIsDropOpen(false);
                      }}
                      color="primary-text"
                      icon={
                        <span className="material-icons" aria-hidden="true">
                          delete
                        </span>
                      }
                    >
                      <Text $theme="primary">{t('Delete the team')}</Text>
                    </Button>
                  )}
                </Box>
              </DropButton>
            )}
          </Box>
        </Box>
        <Box $padding={{ all: '0.5em' }} $direction="row">
          <Text
            $size="s"
            $padding={{ left: '1.5rem' }}
            $display="inline"
            as="p"
          >
            {t('Created at')}&nbsp;
            <Text $weight="bold" $display="inline">
              {created_at}
            </Text>
          </Text>
          <Text
            $size="s"
            $padding={{ left: '1.5rem' }}
            $display="inline"
            as="p"
          >
            {t('Last update at')}&nbsp;
            <Text $weight="bold" $display="inline">
              {updated_at}
            </Text>
          </Text>
        </Box>
      </Box>

      {isModalUpdateOpen && (
        <ModalUpdateTeam
          onClose={() => setIsModalUpdateOpen(false)}
          team={team}
        />
      )}

      {isModalDeleteOpen && (
        <ModalDeleteTeam
          onClose={() => setIsModalDeleteOpen(false)}
          team={team}
        />
      )}
    </>
  );
};
