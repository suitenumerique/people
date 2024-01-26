'use client';

import { CunninghamProvider } from '@openfun/cunningham-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import { useCunninghamTheme } from '@/cunningham';

import '@/i18n/initI18n';
import InnerLayout from './InnerLayout';

import './globals.css';

const queryClient = new QueryClient();

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme } = useCunninghamTheme();

  return (
    <html lang="en">
      <body suppressHydrationWarning={process.env.NODE_ENV === 'development'}>
        <QueryClientProvider client={queryClient}>
          <ReactQueryDevtools />
          <CunninghamProvider theme={theme}>
            <InnerLayout>{children}</InnerLayout>
          </CunninghamProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
