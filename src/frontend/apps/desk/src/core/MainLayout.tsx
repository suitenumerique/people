import { PropsWithChildren } from 'react';

import { Box } from '@/components';
import { Footer } from '@/features/footer/Footer';
import { HEADER_HEIGHT, Header } from '@/features/header';
import { Menu } from '@/features/menu';

export function MainLayout({ children }: PropsWithChildren) {
  return (
    <Box>
      <Box $height="100vh">
        <Header />
        <Box $css="flex: 1;" $direction="row">
          {process.env.NEXT_PUBLIC_FEATURE_TEAM === 'true' && <Menu />}
          <Box
            as="main"
            $height={`calc(100vh - ${HEADER_HEIGHT})`}
            $width="100%"
          >
            {children}
          </Box>
        </Box>
      </Box>
      <Footer />
    </Box>
  );
}
