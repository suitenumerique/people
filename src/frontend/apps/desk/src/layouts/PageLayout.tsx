import { PropsWithChildren } from 'react';

import { Footer } from '@/features/footer';
import { Header } from '@/features/header';

export function PageLayout({ children }: PropsWithChildren) {
  return (
    <div
      style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}
    >
      <Header />
      <main style={{ width: '100%', flexGrow: 1 }}>{children}</main>
      <Footer />
    </div>
  );
}
