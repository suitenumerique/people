'use client';

import { PropsWithChildren } from 'react';

import { Box } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { Panel } from '@/features';

export default function Layout({ children }: PropsWithChildren) {
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
        $css="overflow:auto;"
      >
        {children}
      </Box>
    </Box>
  );
}
