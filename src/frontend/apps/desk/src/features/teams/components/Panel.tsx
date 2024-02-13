import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { PanelActions } from './PanelActions';
import { PanelTeams } from './PanelTeams';

export const Panel = () => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Box
      $width="28rem"
      $css={`
        border-right: 1px solid ${colorsTokens()['primary-300']};
      `}
      $height="inherit"
      aria-label="Teams panel"
    >
      <Box
        className="p-s"
        $direction="row"
        $align="center"
        $justify="space-between"
        $css={`
          border-bottom: 1px solid ${colorsTokens()['primary-300']};
        `}
      >
        <Text $weight="bold" $size="1.25rem">
          {t('Recents')}
        </Text>
        <PanelActions />
      </Box>
      <PanelTeams />
    </Box>
  );
};
