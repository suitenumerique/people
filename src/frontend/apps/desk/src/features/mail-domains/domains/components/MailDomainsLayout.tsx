import { PropsWithChildren } from 'react';

import { Box } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { MainLayout } from '@/layouts';

import { Panel } from './panel';

export function MailDomainsLayout({ children }: PropsWithChildren) {
  const { colorsTokens } = useCunninghamTheme();

  return (
    <MainLayout>
      <Box $height="inherit" $direction="row">
        <Panel />
        <Box
          $background={colorsTokens()['greyscale-050']}
          $width="100%"
          $overflow="auto"
          $height="inherit"
        >
          {children}
        </Box>
      </Box>
    </MainLayout>
  );
}
