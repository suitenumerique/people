'use client';

import { Button } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box } from '@/components';
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
      >
        <StyledButton>{t('Create a new group')}</StyledButton>
      </Box>
    </Box>
  );
}
