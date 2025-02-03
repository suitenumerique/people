import { Button } from '@openfun/cunningham-react';
import Image from 'next/image';
import { useTranslation } from 'react-i18next';
import { css } from 'styled-components';

import { Box, Text, Icon, StyledLink } from '@/components/';
import { ButtonLogin } from '@/core/auth';
import { useCunninghamTheme } from '@/cunningham';
import { LanguagePicker } from '@/features/language';
import { useLeftPanelStore } from '@/features/left-panel';

import { default as IconRegie } from '@/assets/logo-regie.svg?url';

import { LaGaufre } from './LaGaufre';
export const HEADER_HEIGHT = '52px';

export const Header = () => {
  const { t } = useTranslation();
  const theme = useCunninghamTheme();
  const { isPanelOpen, togglePanel } = useLeftPanelStore();

  const spacings = theme.spacingsTokens();
  const colors = theme.colorsTokens();

  return (
    <Box
      as="header"
      $css={`
        display: flex;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        height: var(--header-height);
        min-height: var(--header-height);
        padding: 0 ${spacings['base']};
        background-color: ${colors['greyscale-000']};
        border-bottom: 1px solid ${colors['greyscale-200']};
      `}
    >
        <Button
          className="md:hidden"
          size="medium"
          onClick={() => togglePanel()}
          aria-label={t('Open the header menu')}
          color="tertiary-text"
          icon={
            <Icon
              $variation="800"
              $theme="primary"
              iconName={isPanelOpen ? 'close' : 'menu'}
            />
          }
        />
      <StyledLink href="/">
        <Box
          $align="center"
          $gap={spacings['3xs']}
          $direction="row"
          $position="relative"
          $height="fit-content"
          $margin={{ top: 'auto' }}
        >
          <Image priority src={IconRegie} alt={t('La régie Logo')} width={25} />
           <Box $direction="row" $align="center" $gap="4px">
            <Text $margin="none" as="h2" $color="#000091" $zIndex={1} $size="1.30rem">
              {t('La régie')}
            </Text>
            <Text
              $padding={{ horizontal: '8px', vertical: '1px' }}
              $size="11px"
              $theme="primary"
              $variation="500"
              $weight="bold"
              $radius="12px"
              $background={colors['primary-200']}
            >
              BETA
            </Text>
          </Box>
        </Box>
      </StyledLink>
      <div className="md:hidden">
        <Box $direction="row" $gap={spacings['sm']}>
          <LaGaufre />
        </Box>
      </div>
      <div className="hidden md:block">
        <Box $align="center" $gap={spacings['sm']} $direction="row">
          <ButtonLogin />
          <LanguagePicker />
          <LaGaufre />
        </Box>
      </div>

    </Box>
  );
};