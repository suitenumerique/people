import { PropsWithChildren } from 'react';

import { AppFooter } from '@/components/AppFooter/AppFooter';
import { Header } from '@/features/header';
import { MAIN_LAYOUT_ID } from '@/layouts/conf';

type MainLayoutProps = {
  backgroundColor?: 'white' | 'grey';
  withoutFooter?: boolean;
};

export function MainLayout({ children }: PropsWithChildren<MainLayoutProps>) {
  return (
    <div
      style={{
        backgroundColor: 'var(--c--contextuals--background--surface--primary)',
      }}
    >
      <div
        style={{
          position: 'relative',
          display: 'flex',
          flexDirection: 'row',
          width: '100%',
        }}
      >
        <div
          id={MAIN_LAYOUT_ID}
          style={{
            position: 'relative',
            flex: 1,
            width: '100%',
            height: '100vh',
            overflowY: 'auto',
            overflowX: 'clip',
            paddingBottom: 'var(--app-footer-clearance)',
          }}
        >
          <Header />
          {children}
        </div>
      </div>
      <AppFooter />
    </div>
  );
}
