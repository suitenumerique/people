import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, BoxButton, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import IconOpenClose from '../../assets/icon-open-close.svg';

import { ItemList } from './ItemList';
import { PanelActions } from './PanelActions';

export const Panel = () => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  const [isOpen, setIsOpen] = useState(true);

  const closedOverridingStyles = !isOpen && {
    $width: '0',
    $maxWidth: '0',
    $minWidth: '0',
  };

  const styleNoTeam = process.env.NEXT_PUBLIC_FEATURE_TEAM !== 'true' && {
    $display: 'none',
    tabIndex: -1,
  };

  const transition = 'all 0.5s ease-in-out';

  return (
    <Box
      $width="100%"
      $maxWidth="20rem"
      $minWidth="14rem"
      $css={`
        position: relative;
        border-right: 1px solid ${colorsTokens()['primary-300']};
        transition: ${transition};
      `}
      $height="inherit"
      aria-label="mail domains panel"
      {...closedOverridingStyles}
    >
      <BoxButton
        aria-label={
          isOpen
            ? t(`Close the mail domains panel`)
            : t(`Open the mail domains panel`)
        }
        $color={colorsTokens()['primary-600']}
        $css={`
          position: absolute;
          right: -1.2rem;
          top: 1.03rem;
          transform: rotate(${isOpen ? '0' : '180'}deg);
          transition: ${transition};
        `}
        onClick={() => setIsOpen(!isOpen)}
        {...styleNoTeam}
      >
        <IconOpenClose width={24} height={24} aria-hidden="true" />
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
            border-bottom: 1px solid ${colorsTokens()['primary-300']};
          `}
        >
          <Text $weight="bold" $size="1.25rem">
            {t('Mail Domains')}
          </Text>
          <PanelActions />
        </Box>

        <ItemList />
      </Box>
    </Box>
  );
};
