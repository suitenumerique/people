import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, LogoGouv, StyledLink, Text } from '@/components';
import { useConfigStore } from '@/core';

import frontVersion from '../../../version.json';

import IconLink from './assets/external-link.svg';

const BlueStripe = styled.div`
  position: absolute;
  height: 2px;
  width: 100%;
  background: var(--c--theme--colors--brand-600);
  top: 0;
`;

export const Footer = () => {
  const { t } = useTranslation();
  const { config } = useConfigStore();

  return (
    <Box $position="relative" as="footer">
      <BlueStripe />
      <Box $padding={{ top: 'large', horizontal: 'big', bottom: 'small' }}>
        <Box
          $direction="row"
          $gap="1.5rem"
          $align="center"
          $justify="space-between"
          $css="flex-wrap: wrap;"
        >
          <Box>
            <LogoGouv
              textProps={{
                $size: '1.2rem',
                $margin: { vertical: '0.3rem' },
                $css: `
                  line-height:18px;
                  text-transform: uppercase;
                `,
                $maxWidth: '100px',
              }}
              imagesWidth={66}
            >
              République Française
            </LogoGouv>
          </Box>
          <Box
            $direction="row"
            $css={`
              column-gap: 1.5rem;
              row-gap: .5rem;
              flex-wrap: wrap;
            `}
          >
            {[
              {
                label: 'legifrance.gouv.fr',
                href: 'https://legifrance.gouv.fr/',
              },
              {
                label: 'info.gouv.fr',
                href: 'https://info.gouv.fr/',
              },
              {
                label: 'service-public.fr',
                href: 'https://service-public.fr/',
              },
              {
                label: 'data.gouv.fr',
                href: 'https://data.gouv.fr/',
              },
            ].map(({ label, href }) => (
              <StyledLink
                key={label}
                href={href}
                target="__blank"
                $css={`
                  gap:0.2rem;
                  transition: box-shadow 0.3s;
                  &:hover {
                    box-shadow: 0px 2px 0 0 var(--c--theme--colors--gray-text);
                  }
                `}
              >
                <Text $weight="bold">{label}</Text>
                <IconLink width={18} aria-hidden="true" />
              </StyledLink>
            ))}
          </Box>
        </Box>
        <Box
          $direction="row"
          $margin={{ top: 'big' }}
          $padding={{ top: 'tiny' }}
          $css="
            flex-wrap: wrap;
            border-top: 1px solid var(--c--theme--colors--gray-200);
            column-gap: 1rem;
            row-gap: .5rem;
          "
        >
          {[
            {
              label: t('Legal Notice'),
              href: '/legal-notice',
            },
            {
              label: t('Personal data and cookies'),
              href: '/personal-data-cookies',
            },
            {
              label: t('Accessibility: non-compliant'),
              href: '/accessibility',
            },
          ].map(({ label, href }) => (
            <StyledLink
              key={label}
              href={href}
              $css={`
                padding-right: 1rem;
                &:not(:last-child) {
                  box-shadow: inset -1px 0px 0px 0px var(--c--theme--colors--greyscale-200);
                }
              `}
            >
              <Text
                $variation="600"
                $size="m"
                $css={`
                  transition: box-shadow 0.3s;
                  &:hover {
                    box-shadow: 0px 2px 0 0 var(--c--theme--colors--greyscale-text);
                  }
                `}
              >
                {label}
              </Text>
            </StyledLink>
          ))}
        </Box>

        <Text as="p" aria-hidden="true" $css="display: none">
          You have found the hidden app version information ! Well done ! back
          commit is: {config?.COMMIT}; front commit is: {frontVersion?.commit}
        </Text>

        <Text
          as="p"
          $size="m"
          $margin={{ top: 'big' }}
          $variation="600"
          $display="inline"
        >
          {config?.RELEASE && (
            <>
              {t(`Version: {{release}}`, { release: config?.RELEASE })} •&nbsp;
            </>
          )}

          <Trans>
            Unless otherwise stated, all content on this site is under
            <StyledLink
              href="https://github.com/etalab/licence-ouverte/blob/master/LO.md"
              target="__blank"
              $css={`
                display:inline-flex;
                box-shadow: 0px 1px 0 0 var(--c--theme--colors--greyscale-text);
                margin-left: 0.3rem;
              `}
            >
              <Text $variation="600">licence etalab-2.0</Text>
              <IconLink width={18} aria-hidden="true" />
            </StyledLink>
          </Trans>
        </Text>
      </Box>
    </Box>
  );
};
