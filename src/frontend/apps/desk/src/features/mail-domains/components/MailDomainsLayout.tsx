import { PropsWithChildren } from 'react';

import { Box } from '@/components';
import { MainLayout } from '@/core';
import { useCunninghamTheme } from '@/cunningham';
import { Panel } from '@/features/mail-domains/components/panel';

export function MailDomainsLayout({ children }: PropsWithChildren) {
  const { colorsTokens } = useCunninghamTheme();

  return (
    <MainLayout>
      <Box $height="inherit" $direction="row">
        <Panel />
        <Box
          $background={colorsTokens()['primary-bg']}
          $width="100%"
          $height="inherit"
        >
          {children}
        </Box>
      </Box>
    </MainLayout>
  );
}
