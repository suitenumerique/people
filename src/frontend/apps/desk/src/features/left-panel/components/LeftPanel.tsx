import { usePathname } from 'next/navigation';
import { useCallback, useEffect } from 'react';
import { createGlobalStyle } from 'styled-components';
import { default as IconRegie } from '@/assets/logo-regie.svg?url';
import { StyledLink } from '@/components/';
import Image from 'next/image';

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

  // Desktop : panneau ouvert par défaut au premier rendu
  useEffect(() => {
    if (typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches) {
      togglePanel(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Mobile : fermer le panneau à chaque changement de route
  useEffect(() => {
    if (typeof window !== 'undefined' && !window.matchMedia('(min-width: 768px)').matches) {
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
            transform: `translateX(${isPanelOpen ? '0' : '-100dvw'})`,
          }}
          className="md:hidden"
        >
          <div
            data-testid="left-panel-mobile"
            style={{
              width: '100%',
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
