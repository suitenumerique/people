import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import IconOpenClose from '@/assets/icons/icon-open-close.svg';
import { Box, BoxButton, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { PanelActions } from './PanelActions';
import { TeamList } from './TeamList';

export const Panel = () => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  const [isOpen, setIsOpen] = useState(true);

  const closedOverridingStyles = !isOpen && {
    $width: '0',
    $maxWidth: '0',
    $minWidth: '0',
  };

  const transition = 'all 0.5s ease-in-out';

  return (
    <Box
      $width="100%"
      $maxWidth="20rem"
      $minWidth="14rem"
      $css={`
        position: relative;
        border-right: 1px solid ${colorsTokens()['brand-300']};
        transition: ${transition};
      `}
      $height="inherit"
      aria-label="Teams panel"
      {...closedOverridingStyles}
    >
      <BoxButton
        aria-label={
          isOpen ? t('Close the teams panel') : t('Open the teams panel')
        }
        $color={colorsTokens()['brand-600']}
        $css={`
          position: absolute;
          right: -1.2rem;
          top: 1.03rem;
          transform: rotate(${isOpen ? '0' : '180'}deg);
          transition: ${transition};
        `}
        onClick={() => setIsOpen(!isOpen)}
      >
        <IconOpenClose width={24} height={24} />
      </BoxButton>
      <Box
        $css={`
          overflow: hidden;
          opacity: ${isOpen ? '1' : '0'};
          transition: ${transition};
        `}
      >
        <Box
          $padding={{ all: 'small', right: 'large' }}
          $direction="row"
          $align="center"
          $justify="space-between"
          $css={`
            border-bottom: 1px solid ${colorsTokens()['brand-300']};
          `}
        >
          <Text $weight="bold" $size="1.25rem">
            {t('Groups')}
          </Text>
          <PanelActions />
        </Box>
        <TeamList />
      </Box>
    </Box>
  );
};
