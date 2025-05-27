import type { AppProps } from 'next/app';
import Head from 'next/head';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import { AppProvider, useConfigStore } from '@/core';
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
  const { config } = useConfigStore();

  useEffect(() => {
    if (!window.$crisp && config?.CRISP_WEBSITE_ID) {
      window.$crisp = [];
      window.CRISP_WEBSITE_ID = config?.CRISP_WEBSITE_ID;

      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.async = true;
      script.src = 'https://client.crisp.chat/l.js';
      document.head.appendChild(script);
    }
  }, [config]);

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
