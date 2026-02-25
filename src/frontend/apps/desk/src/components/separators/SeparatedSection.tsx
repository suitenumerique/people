import { PropsWithChildren } from 'react';
import { css } from 'styled-components';

import { Box } from '../Box';

type Props = {
  showSeparator?: boolean;
};

export const SeparatedSection = ({
  showSeparator = true,
  children,
}: PropsWithChildren<Props>) => {
  return (
    <Box
      $css={css`
        width: 100%;
        ${showSeparator &&
        css`
          border-bottom: 1px solid
            var(--c--contextuals--border--surface--primary);
        `}
      `}
    >
      {children}
    </Box>
  );
};
