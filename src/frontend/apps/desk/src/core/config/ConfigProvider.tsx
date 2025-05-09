import { Loader } from '@openfun/cunningham-react';
import { PropsWithChildren, useEffect } from 'react';
import { configureCrispSession } from '@/services';
import { Box } from '@/components';

import { useConfigStore } from './useConfigStore';

export const ConfigProvider = ({ children }: PropsWithChildren) => {
  const { config, initConfig } = useConfigStore();

  useEffect(() => {
    initConfig();
  }, [initConfig]);

  useEffect(() => {
    if (!config?.CRISP_WEBSITE_ID) {
      return;
    }

    configureCrispSession(conf.CRISP_WEBSITE_ID);
  }, [config?.CRISP_WEBSITE_ID]);

  if (!config) {
    return (
      <Box $height="100vh" $width="100vw" $align="center" $justify="center">
        <Loader />
      </Box>
    );
  }

  return children;
};
