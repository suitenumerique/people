'use client';

import { Button } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, StyledLink } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { Panel } from '@/features';

const StyledButton = styled(Button)`
  width: fit-content;
`;

export default function Home() {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Box $height="inherit" $direction="row">
      <Panel />
      <Box
        $background={colorsTokens()['primary-bg']}
        $justify="center"
        $align="center"
        $width="100%"
        $gap="5rem"
      >
        <StyledLink href="/teams/create">
          <StyledButton>{t('Create a new team')}</StyledButton>
        </StyledLink>
      </Box>
    </Box>
  );
}
