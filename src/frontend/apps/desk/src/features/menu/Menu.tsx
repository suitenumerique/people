import React from 'react';
import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group.svg';
import { Box } from '@/components/';
import useCunninghamTheme from '@/cunningham/useCunninghamTheme';

import MenuItem from './MenuItems';
import IconMail from './assets/icon-mails.svg';

export const Menu = () => {
  const { colorsTokens } = useCunninghamTheme();
  const { t } = useTranslation();

  return (
    <Box
      as="menu"
      $background={colorsTokens()['primary-800']}
      $height="100%"
      $justify="space-between"
      $padding="none"
      $margin="none"
    >
      <Box $padding={{ top: 'large' }} $direction="column" $gap="0.8rem">
        <MenuItem Icon={IconGroup} label={t('Teams')} href="/" />
        <MenuItem Icon={IconMail} label={t('Mails')} href="/mails" />
      </Box>
    </Box>
  );
};
