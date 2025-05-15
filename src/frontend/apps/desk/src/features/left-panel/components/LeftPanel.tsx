import { usePathname } from 'next/navigation';
import { useCallback, useEffect } from 'react';
import { createGlobalStyle } from 'styled-components';

import { SeparatedSection } from '@/components/separators';
import { ButtonLogin } from '@/core';
import { UserInfo } from '@/core/auth/UserInfo';
import { LanguagePicker } from '@/features/language';

import { useLeftPanelStore } from '../stores';

import { LeftPanelContent } from './LeftPanelContent';
import { LeftPanelHeader } from './LeftPanelHeader';
import { LeftPanelItems } from './LeftPanelItems';

const MobileLeftPanelStyle = createGlobalStyle`
  body {
    overflow: hidden;
  }
`;

const LeftPanelStyle = createGlobalStyle`
  .LeftPanel {
    height: calc(100vh - var(--header-height));
    width: 300px;
    min-width: 300px;
    overflow: hidden;
    border-right: 1px solid var(--c--theme--colors--greyscale-200']};
  }
`;

export const LeftPanel = () => {
  const { togglePanel, isPanelOpen } = useLeftPanelStore();

  const pathname = usePathname();

  const toggle = useCallback(() => {
    togglePanel(false);
  }, [togglePanel]);

  useEffect(() => {
    toggle();
  }, [pathname, toggle]);

  return (
    <>
      <div className="hidden md:block">
        <LeftPanelStyle />
        <div className="LeftPanel">
          <div
            style={{
              flex: '0 0 auto',
            }}
          ></div>
          <menu
            style={{
              margin: '0',
              gap: 'var(--c--theme--spacings--xs)',
              padding: '0 10px',
            }}
          >
            <LeftPanelItems />
          </menu>
          <LeftPanelContent />
        </div>
      </div>

      <>
        {isPanelOpen && <MobileLeftPanelStyle />}
        <div
          style={{
            zIndex: '999',
            width: '100vw',
            height: 'calc(100dvh - var(--header-height))',
            borderRight: '1px solid var(--c--theme--colors--greyscale-200)',
            position: 'fixed',
            transform: `translateX(${isPanelOpen ? '0' : '-100dvw'})`,
            backgroundColor: 'var(--c--theme--colors--greyscale-000)',
          }}
          className="md:hidden"
        >
          <div
            data-testid="left-panel-mobile"
            style={{
              width: '100%',
              padding: '0 10px',
              justifyContent: 'center',
              gap: 'var(--c--theme--spacings--base)',
            }}
            className="md:hidden"
          >
            <LeftPanelHeader />
            <LeftPanelItems />
            <SeparatedSection showSeparator={false}>
              <div
                style={{
                  display: 'flex',
                  alignSelf: 'center',
                  flexDirection: 'column',
                  gap: 'var(--c--theme--spacings--sm)',
                }}
              >
                <UserInfo />
                <ButtonLogin />
                <LanguagePicker />
              </div>
            </SeparatedSection>
          </div>
        </div>
      </>
    </>
  );
};
