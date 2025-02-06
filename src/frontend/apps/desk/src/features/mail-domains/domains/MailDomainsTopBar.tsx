import { PropsWithChildren } from 'react';

import { Box } from '@/components';

export function MailDomainsTopBar({ children }: PropsWithChildren) {
  const { colorsTokens } = useCunninghamTheme();

  return (
      <Box $height="inherit" $direction="row">
      COUCOU
      </Box>
  );
}
