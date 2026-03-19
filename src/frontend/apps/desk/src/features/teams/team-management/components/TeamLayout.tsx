import { PropsWithChildren } from 'react';

import { Box } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { Panel } from '@/features/teams/teams-panel';
import { MainLayout } from '@/layouts';

export function TeamLayout({ children }: PropsWithChildren) {
  const { colorsTokens } = useCunninghamTheme();

  return (
    <MainLayout>
      <Box $height="inherit" $direction="row">
        <Panel />
        <Box
          $background={colorsTokens()['gray-050']}
          $width="100%"
          $height="inherit"
        >
          {children}
        </Box>
      </Box>
    </MainLayout>
  );
}
