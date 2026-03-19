import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useCallback, useEffect } from 'react';
import { createGlobalStyle } from 'styled-components';

import { default as IconRegie } from '@/assets/logo-regie.svg?url';
import { StyledLink } from '@/components/';
import { SeparatedSection } from '@/components/separators';

import { useLeftPanelStore } from '../stores';

import { LeftPanelContent } from './LeftPanelContent';
import { LeftPanelItems } from './LeftPanelItems';

const MobileLeftPanelStyle = createGlobalStyle`
  body {
    overflow: hidden;
  }
`;

const LeftPanelStyle = createGlobalStyle`
  .LeftPanel {
    position: sticky;
    top: 0;
    padding: 12px;
    height: 100vh;
    width: 300px;
    min-width: 300px;
    overflow: hidden;
    background-color: var(--c--contextuals--background--surface--tertiary);
    border-right: 1px solid var(--c--contextuals--border--surface--primary);
  }
`;

export const LeftPanel = () => {
  const { togglePanel, isPanelOpen } = useLeftPanelStore();

  const pathname = usePathname();

  const closePanel = useCallback(() => {
    togglePanel(false);
  }, [togglePanel]);

  useEffect(() => {
    if (
      typeof globalThis.window !== 'undefined' &&
      globalThis.window.matchMedia('(min-width: 768px)').matches
    ) {
      togglePanel(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (
      typeof globalThis.window !== 'undefined' &&
      !globalThis.window.matchMedia('(min-width: 768px)').matches
    ) {
      closePanel();
    }
  }, [pathname, closePanel]);

  return (
    <>
      <div
        className="hidden md:block"
        style={{
          width: isPanelOpen ? undefined : 0,
          minWidth: isPanelOpen ? undefined : 0,
          overflow: 'hidden',
          transition: 'min-width 0.2s ease, width 0.2s ease',
        }}
      >
        <LeftPanelStyle />
        <div className="LeftPanel" style={{ minWidth: isPanelOpen ? 300 : 0 }}>
          <div
            style={{
              flex: '0 0 auto',
            }}
          ></div>
          <StyledLink href="/">
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '1rem',
              }}
            >
              <Image priority src={IconRegie} alt="Régie" height={40} />
            </div>
          </StyledLink>
          <menu
            style={{
              margin: '0',
              gap: 'var(--c--theme--spacings--xs)',
              padding: '0',
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
            height: '100vh',
            position: 'fixed',
            inset: 0,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'flex-start',
            padding: '12px',
            backgroundColor:
              'var(--c--contextuals--background--surface--tertiary)',
            transform: `translateX(${isPanelOpen ? '0' : '-100dvw'})`,
            transition: 'transform 0.2s ease-out',
            overflowY: 'auto',
          }}
          className="md:hidden"
        >
          <div
            data-testid="left-panel-mobile"
            style={{
              width: '100%',
              marginTop: '60px',
              justifyContent: 'flex-start',
              gap: 'var(--c--theme--spacings--base)',
            }}
            className="md:hidden"
          >
            <StyledLink href="/">
              <div>
                <Image priority src={IconRegie} alt="Régie" height={40} />
              </div>
            </StyledLink>
            <LeftPanelItems />
            <SeparatedSection showSeparator={false}>
              <div
                style={{
                  display: 'flex',
                  alignSelf: 'center',
                  flexDirection: 'column',
                  gap: 'var(--c--theme--spacings--sm)',
                }}
              ></div>
            </SeparatedSection>
          </div>
        </div>
      </>
    </>
  );
};
