import { PropsWithChildren } from 'react';

import { Box } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { Panel } from '@/features/teams';

import MainLayout from '../MainLayout';

export default function TeamLayout({ children }: PropsWithChildren) {
  const { colorsTokens } = useCunninghamTheme();

  return (
    <MainLayout>
      <Box $height="inherit" $direction="row">
        <Panel />
        <Box
          $background={colorsTokens()['primary-bg']}
          $justify="center"
          $align="center"
          $width="100%"
          $gap="5rem"
          $css="overflow:auto;"
        >
          {children}
        </Box>
      </Box>
    </MainLayout>
  );
}
