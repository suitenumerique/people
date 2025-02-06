import { usePathname } from 'next/navigation';
import { useCallback, useEffect } from 'react';
import { createGlobalStyle, css } from 'styled-components';

import { Box } from '@/components';
import { SeparatedSection } from '@/components/separators';
import { ButtonLogin } from '@/core';
import { useCunninghamTheme } from '@/cunningham';
import { LanguagePicker } from '@/features/language';

import { useLeftPanelStore } from '../stores';

import { LeftPanelContent } from './LeftPanelContent';
import { LeftPanelHeader } from './LeftPanelHeader';
import { LeftPanelTargetFilters } from './LeftPanelTargetFilters';

const MobileLeftPanelStyle = createGlobalStyle`
  body {
    overflow: hidden;
  }
`;

export const LeftPanel = () => {

  const theme = useCunninghamTheme();
  const { togglePanel, isPanelOpen } = useLeftPanelStore();

  const pathname = usePathname();
  const colors = theme.colorsTokens();
  const spacings = theme.spacingsTokens();

  const toggle = useCallback(() => {
    togglePanel(false);
  }, [togglePanel]);

  useEffect(() => {
    toggle();
  }, [pathname, toggle]);

  return (
    <>
      <div className="hidden md:block">
        <Box
          data-testid="left-panel-desktop"
          $css={`
            height: calc(100vh - var(--header-height));
            width: 300px;

            min-width: 300px;
            overflow: hidden;
            border-right: 1px solid ${colors['greyscale-200']};
        `}
        >
          <Box
            $css={css`
              flex: 0 0 auto;
            `}
          >
          </Box>
          <LeftPanelTargetFilters />
           <LeftPanelContent />
        </Box>
      </div>


        <>
          {isPanelOpen && <MobileLeftPanelStyle />}
          <Box
            $hasTransition
            $css={css`
              z-index: 999;
              width: 100dvw;
              height: calc(100dvh - var(--header-height));
              border-right: 1px solid var(--c--theme--colors--greyscale-200);
              position: fixed;
              transform: translateX(${isPanelOpen ? '0' : '-100dvw'});
              background-color: var(--c--theme--colors--greyscale-000);
            `}
            className="md:hidden"
          >
            <Box
              data-testid="left-panel-mobile"
              $css={css`
                width: 100%;
                justify-content: center;
                gap: ${spacings['base']};
              `}
              className="md:hidden"
            >
              <LeftPanelHeader />
              <LeftPanelTargetFilters />
              <LeftPanelContent />
              <SeparatedSection showSeparator={false}>
                <Box $justify="center" $align="center" $gap={spacings['sm']}>
                  <ButtonLogin />
                  <LanguagePicker />
                </Box>
              </SeparatedSection>
            </Box>
          </Box>
        </>
    </>
  );
};