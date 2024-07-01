import { Head, Html, Main, NextScript } from 'next/document';

import '@/i18n/initI18n';

export default function RootLayout() {
  return (
    <Html>
      <Head />
      <body suppressHydrationWarning={process.env.NODE_ENV === 'development'}>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
