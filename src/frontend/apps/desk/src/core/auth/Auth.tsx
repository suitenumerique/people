import { Loader } from '@openfun/cunningham-react';
import { useRouter } from 'next/router';
import { PropsWithChildren, useEffect } from 'react';

import { Box } from '@/components';

import { useAuthStore } from './useAuthStore';

export const Auth = ({ children }: PropsWithChildren) => {
  const { authenticated, initAuth } = useAuthStore();
  const router = useRouter();
  const isLoginPage = router.pathname === '/login';

  useEffect(() => {
    if (!isLoginPage) {
      initAuth();
    }
  }, [initAuth, isLoginPage]);

  if (!authenticated && !isLoginPage) {
    return (
      <Box $height="100vh" $width="100vw" $align="center" $justify="center">
        <Loader />
      </Box>
    );
  }

  return children;
};
