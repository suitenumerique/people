import { PropsWithChildren } from 'react';

import { Footer } from '@/features/footer';
import { HEADER_HEIGHT, Header } from '@/features/header';
import { LeftPanel } from '@/features/left-panel';
import { MAIN_LAYOUT_ID } from '@/layouts/conf';

type MainLayoutProps = {
  backgroundColor?: 'white' | 'grey';
  withoutFooter?: boolean;
};

export function MainLayout({
  children,
  backgroundColor = 'white',
  withoutFooter = false,
}: PropsWithChildren<MainLayoutProps>) {
  return (
    <div
      style={{
        backgroundColor: 'var(--c--contextuals--background--surface--tertiary)'
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
        <LeftPanel />
        <div
          id={MAIN_LAYOUT_ID}
          style={{
            position: 'relative',
            flex: 1,
            width: '100%',
            height: '100vh',
            overflowY: 'auto',
            overflowX: 'clip',
          }}
        >
          <Header />
          {children}
        </div>
      </div>
    </div>
  );
}
