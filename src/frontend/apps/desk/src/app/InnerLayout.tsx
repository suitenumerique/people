import { Loader } from '@openfun/cunningham-react';
import { useEffect } from 'react';

import useAuthStore from '@/auth/useAuthStore';
import { Box } from '@/components';

import { HEADER_HEIGHT, Header } from './header';
import { Menu } from './menu';

export default function InnerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { initAuth, authenticated, initialized } = useAuthStore();

  useEffect(() => {
    if (initialized) {
      return;
    }

    initAuth();
  }, [initAuth, initialized]);

  if (!authenticated) {
    return (
      <Box $height="100vh" $width="100vw" $align="center" $justify="center">
        <Loader />
      </Box>
    );
  }

  return (
    <Box as="main" $direction="column" $height="100vh" $css="overflow:hidden;">
      <Header />
      <Box $css="flex: 1;">
        <Menu />
        <Box
          $direction="column"
          $height={`calc(100vh - ${HEADER_HEIGHT})`}
          $width="100%"
          $css="overflow: auto;"
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
