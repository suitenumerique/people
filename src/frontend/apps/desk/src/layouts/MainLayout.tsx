import { PropsWithChildren } from 'react';

import { useCunninghamTheme } from '@/cunningham';
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
  const { colorsTokens } = useCunninghamTheme();
  const colors = colorsTokens();

  return (
    <div>
      <Header />
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          marginTop: HEADER_HEIGHT,
          width: '100%',
        }}
      >
        <LeftPanel />
        <div
          id={MAIN_LAYOUT_ID}
          style={{
            flex: 1,
            width: '100%',
            height: `calc(100dvh - ${HEADER_HEIGHT})`,
            backgroundColor:
              backgroundColor === 'white'
                ? colors['greyscale-000']
                : colors['greyscale-050'],
            overflowY: 'auto',
            overflowX: 'clip',
          }}
        >
          {children}
        </div>
      </div>
      {!withoutFooter && <Footer />}
    </div>
  );
}
