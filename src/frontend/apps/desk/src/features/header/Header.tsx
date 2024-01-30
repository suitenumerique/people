import { Button } from '@openfun/cunningham-react';
import Image from 'next/image';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, Text } from '@/components/';

import { LanguagePicker } from '../language/';

import { default as IconCells } from './assets/icon-cells.svg?url';
import { default as IconDesk } from './assets/icon-desk.svg?url';
import { default as IconFAQ } from './assets/icon-faq.svg?url';
import { default as IconGouv } from './assets/icon-gouv.svg?url';
import { default as IconMarianne } from './assets/icon-marianne.svg?url';
import IconMyAccount from './assets/icon-my-account.png';

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
      <Box className="ml-bx mr-bx" $align="center" $justify="space-between">
        <Box $direction="column">
          <Image priority src={IconMarianne} alt={t('Marianne Logo')} />
          <Box $align="center" $gap="6rem">
            <Image
              priority
              src={IconGouv}
              alt={t('Freedom Equality Fraternity Logo')}
            />
            <Box $align="center" $gap="1rem">
              <Image priority src={IconDesk} alt={t('Desk Logo')} />
              <Text className="m-0" as="h2">
                {t('Desk')}
              </Text>
            </Box>
          </Box>
        </Box>
        <Box
          $align="center"
          $css={`
            & > button {
              padding: 0;
            }
          `}
          $gap="5rem"
          $justify="flex-end"
        >
          <Box $align="center">
            <Button
              aria-label={t('Access to FAQ')}
              icon={<Image priority src={IconFAQ} alt={t('FAQ Icon')} />}
              className="m-s c__button-no-bg p-0"
            >
              {t('FAQ')}
            </Button>
            <LanguagePicker />
          </Box>
          <Box>
            <Box $direction="row" $align="center" $gap="1rem">
              <Text $weight="bold">John Doe</Text>
              <Image
                width={58}
                height={58}
                priority
                src={IconMyAccount}
                alt={t(`Profile picture`)}
                unoptimized
              />
            </Box>
            <Button
              aria-label={t('Access to the cells menu')}
              icon={<Image priority src={IconCells} alt={t('Cells icon')} />}
              color="tertiary"
              className="c__button-no-bg p-0 m-0"
            />
          </Box>
        </Box>
      </Box>
    </StyledHeader>
  );
};
