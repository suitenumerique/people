import { PropsWithChildren } from 'react';

import { Box } from '@/components';
import { Footer } from '@/features/footer/Footer';
import { Header } from '@/features/header';

export function LoginLayout({ children }: PropsWithChildren) {
  return (
    <Box>
      <Box $height="100vh">
        <Header />
        <Box $css="flex: 1;" $direction="row">
          {children}
        </Box>
        <Footer />
      </Box>
    </Box>
  );
}
