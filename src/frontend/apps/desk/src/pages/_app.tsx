import type { AppProps } from 'next/app';
import Head from 'next/head';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { AppProvider } from '@/core/';
import { NextPageWithLayout } from '@/types/next';

import './globals.css';

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

declare global {
  interface Window {
    $crisp?: Array<[]>;
    CRISP_WEBSITE_ID?: string;
  }
}

export default function App({ Component, pageProps }: AppPropsWithLayout) {
  const getLayout = Component.getLayout ?? ((page) => page);
  const { t } = useTranslation();

  useEffect(() => {
    if (!window.$crisp) {
      window.$crisp = [];
      window.CRISP_WEBSITE_ID = '58ea6697-8eba-4492-bc59-ad6562585041';

      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.async = true;
      script.src = 'https://client.crisp.chat/l.js';
      document.head.appendChild(script);
    }
  }, []);

  return (
    <>
      <Head>
        <title>{t('La Régie')}</title>
        <meta
          name="description"
          content={t(
            'La Suite administration interface: management of users and rights on the various tools (messaging, storage, etc.)',
          )}
        />
        <link rel="icon" href="/favicon.ico" sizes="any" />
      </Head>
      <AppProvider>{getLayout(<Component {...pageProps} />)}</AppProvider>
    </>
  );
}
