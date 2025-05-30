import type { AppProps } from 'next/app';
import Head from 'next/head';
import { useTranslation } from 'react-i18next';

import { AppProvider } from '@/core/';
import { NextPageWithLayout } from '@/types/next';

import './globals.css';

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

export default function App({ Component, pageProps }: AppPropsWithLayout) {
  const getLayout = Component.getLayout ?? ((page) => page);
  const { t } = useTranslation();

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
