import Head from 'next/head';
import Script from 'next/script';
import React from 'react';

/**
 * ApplicationsMenu Component
 *
 * This component is a work in progress (WIP) and serves as a proof of concept (POC) to showcase a future advanced feature.
 * The purpose of this component is to render an applications menu for La Suite, allowing users to switch between different La Suite apps seamlessly.
 * To ensure synchronized content across applications, it utilizes an iframe hosted on Scalingo.
 *
 * This PoC has been created by @manuhabitela.
 *
 * It includes external CSS and JavaScript files for styling and functionality.
 */
export const ApplicationsMenu = () => (
  <>
    <Head>
      <link
        rel="stylesheet"
        href="https://suite-numerique-gaufre.osc-fr1.scalingo.io/public/styles/gaufre-vanilla.css"
      />
    </Head>
    <Script
      src="https://suite-numerique-gaufre.osc-fr1.scalingo.io/public/widget.js"
      strategy="lazyOnload"
    />
    <button
      style={{ marginLeft: '1.5rem', verticalAlign: 'center' }}
      type="button"
      className="lasuitenumerique-gaufre-btn lasuitenumerique-gaufre-btn--vanilla"
      title="Les applications de La Suite numérique"
    >
      Les applications de La Suite numérique
    </button>
  </>
);
