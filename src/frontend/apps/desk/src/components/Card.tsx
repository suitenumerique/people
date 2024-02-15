import { PropsWithChildren } from 'react';

import { useCunninghamTheme } from '@/cunningham';

import { Box, BoxType } from '.';

export const Card = ({
  children,
  $css,
  ...props
}: PropsWithChildren<BoxType>) => {
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Box
      $background="white"
      $radius="4px"
      $css={`
        box-shadow: 2px 2px 5px ${colorsTokens()['primary-300']}88;
        border: 1px solid #e3e3e3;
        ${$css}
      `}
      {...props}
    >
      {children}
    </Box>
  );
};
