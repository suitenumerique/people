import { useRouter } from 'next/router';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, StyledLink, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import IconMailDomains from '@/features/mail-domains/assets/icon-mail-domains.svg';

import { MailDomain } from '../../index';

interface MailDomainProps {
  mailDomain: MailDomain;
}

export const PanelMailDomains = ({ mailDomain }: MailDomainProps) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();
  const {
    query: { slug },
  } = useRouter();

  const isActive = mailDomain.slug === slug;

  const getStatusText = (status: MailDomain['status']) => {
    switch (status) {
      case 'pending':
        return t('[pending]');
      case 'enabled':
        return t('[enabled]');
      case 'disabled':
        return t('[disabled]');
      case 'failed':
        return t('[failed]');
      case 'action_required':
        return t('[action required]');
    }
  };

  const activeStyle = `
    border-right: 4px solid ${colorsTokens()['primary-600']};
    background: ${colorsTokens()['primary-400']};
     span {
      color: ${colorsTokens()['primary-text']};
    }
  `;

  const hoverStyle = `
    &:hover{
      border-right: 4px solid ${colorsTokens()['primary-400']};
      background: ${colorsTokens()['primary-300']};

       span {
        color: ${colorsTokens()['primary-text']};
      }
    }
  `;

  const statusText = getStatusText(mailDomain.status);

  return (
    <Box
      $margin="none"
      as="li"
      $css={`
        transition: all 0.2s ease-in; 
        border-right: 4px solid transparent;
        ${isActive ? activeStyle : hoverStyle}
      `}
    >
      <StyledLink
        className="p-s pt-t pb-t"
        $css="width: 100%"
        href={`/mail-domains/${mailDomain.slug}`}
      >
        <Box
          $position="relative"
          $align="center"
          $direction="row"
          $justify="space-between"
          $gap="1rem"
        >
          <Box $direction="row" $gap="0.5rem" $justify="left" $align="center">
            <IconMailDomains
              aria-hidden="true"
              color={colorsTokens()['primary-500']}
              className="p-t"
              width="52"
              style={{
                borderRadius: '10px',
                flexShrink: 0,
                background: '#fff',
                border: `1px solid ${colorsTokens()['primary-300']}`,
              }}
            />
            <Text
              $weight="bold"
              $color={colorsTokens()['greyscale-600']}
              $css={`
              display: inline-block;
              width: 10rem;
              overflow: hidden;
              text-overflow: ellipsis !important;
            `}
            >
              {mailDomain.name}
            </Text>
          </Box>
          <Text $size="s" $theme="greyscale">
            {statusText}
          </Text>
        </Box>
      </StyledLink>
    </Box>
  );
};
