import Image from 'next/image';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, Text } from '@/components/';
import { AccountDropdown } from '@/features/header/AccountDropdown';
import { ApplicationsMenu } from '@/features/header/ApplicationsMenu';

import { LanguagePicker } from '../language/';

import { default as IconApplication } from './assets/icon-application.svg?url';
import { default as IconGouv } from './assets/icon-gouv.svg?url';
import { default as IconMarianne } from './assets/icon-marianne.svg?url';

export const HEADER_HEIGHT = '100px';

const RedStripe = styled.div`
  position: absolute;
  height: 5px;
  width: 100%;
  background: var(--c--theme--colors--danger-500);
  top: 0;
`;

const StyledHeader = styled.header`
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: ${HEADER_HEIGHT};
  width: 100%;
  background: white;
  box-shadow: 0 1px 4px #00000040;
  z-index: 100;
`;

export const Header = () => {
  const { t } = useTranslation();

  return (
    <StyledHeader>
      <RedStripe />
      <Box
        $margin={{ horizontal: 'xbig' }}
        $align="center"
        $justify="space-between"
        $direction="row"
      >
        <Box>
          <Image priority src={IconMarianne} alt={t('Marianne Logo')} />
          <Box $align="center" $gap="6rem" $direction="row">
            <Image
              priority
              src={IconGouv}
              alt={t('Freedom Equality Fraternity Logo')}
            />
            <Box $align="center" $gap="1rem" $direction="row">
              <Image priority src={IconApplication} alt={t('Equipes Logo')} />
              <Text $margin="none" as="h2" $theme="primary">
                {t('Equipes')}
              </Text>
            </Box>
          </Box>
        </Box>
        <Box $align="center" $gap="1rem" $justify="flex-end" $direction="row">
          <AccountDropdown />
          <LanguagePicker />
          <ApplicationsMenu />
        </Box>
      </Box>
    </StyledHeader>
  );
};
