import { Loader } from '@openfun/cunningham-react';
import React from 'react';
import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group.svg';
import { Box, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { useTeams } from '../api/useTeams';
import IconNone from '../assets/icon-none.svg';

export const PanelTeams = () => {
  const { data, isPending, isError } = useTeams();
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  if (isPending) {
    return (
      <Box $align="center" className="m-l">
        <Loader />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box $justify="center" className="m-b">
        <Text $theme="danger" $align="center" $textAlign="center">
          {t('Something bad happens, please refresh the page.')}
        </Text>
      </Box>
    );
  }

  if (!data.count) {
    return (
      <Box $justify="center" className="m-b">
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

  return (
    <Box as="ul" $gap="1rem" className="p-s mt-t">
      {data?.results.map((team) => (
        <Box
          as="li"
          key={team.id}
          $direction="row"
          $align="center"
          $gap="0.5rem"
        >
          {team.accesses.length ? (
            <IconGroup
              className="p-t"
              width={36}
              aria-label={t(`Team icon`)}
              color={colorsTokens()['primary-500']}
              style={{
                borderRadius: '10px',
                border: `1px solid ${colorsTokens()['primary-300']}`,
              }}
            />
          ) : (
            <IconNone
              className="p-t"
              width={36}
              aria-label={t(`Empty team icon`)}
              color={colorsTokens()['greyscale-500']}
              style={{
                borderRadius: '10px',
                border: `1px solid ${colorsTokens()['greyscale-300']}`,
              }}
            />
          )}
          <Text $weight="bold">{team.name}</Text>
        </Box>
      ))}
    </Box>
  );
};
