import { PropsWithChildren } from 'react';

import { AppFooter } from '@/components/AppFooter/AppFooter';
import { Footer } from '@/features/footer';
import { Header } from '@/features/header';

export function PageLayout({ children }: PropsWithChildren) {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        paddingBottom: 'var(--app-footer-clearance)',
      }}
    >
      <Header />
      <main style={{ width: '100%', flexGrow: 1 }}>{children}</main>
      <Footer />
      <AppFooter />
    </div>
  );
}
