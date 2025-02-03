import { useRouter } from 'next/router';
import { css } from 'styled-components';

import { Box, SeparatedSection } from '@/components';

export const LeftPanelContent = () => {
  const router = useRouter();
  const isHome = router.pathname === '/';

  return (
    <>
      {isHome && (
        <>
          <Box
            $width="100%"
            $css={css`
              flex: 0 0 auto;
            `}
          >
            <SeparatedSection showSeparator={false}>
            </SeparatedSection>
          </Box>
          <Box
            $flex={1}
            $width="100%"
            $css="overflow-y: auto; overflow-x: hidden;"
          >
          </Box>
          <div> Coucou </div>
        </>
      )}
    </>
  );
};