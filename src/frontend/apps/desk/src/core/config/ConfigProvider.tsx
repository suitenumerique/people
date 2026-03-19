import { Loader } from '@gouvfr-lasuite/cunningham-react';
import { PropsWithChildren, useEffect } from 'react';

import { Box } from '@/components';

import { useConfigStore } from './useConfigStore';

export const ConfigProvider = ({ children }: PropsWithChildren) => {
  const { config, initConfig } = useConfigStore();

  useEffect(() => {
    initConfig();
  }, [initConfig]);

  if (!config) {
    return (
      <Box $height="100vh" $width="100vw" $align="center" $justify="center">
        <Loader />
      </Box>
    );
  }

  return children;
};
