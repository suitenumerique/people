import { Loader } from '@openfun/cunningham-react';
import { PropsWithChildren, useEffect } from 'react';

import { Box } from '@/components';

import { useAuthStore } from './useAuthStore';

export const Auth = ({ children }: PropsWithChildren) => {
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

  return children;
};
