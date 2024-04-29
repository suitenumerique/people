import React from 'react';
import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group.svg';
import { Box } from '@/components/';
import useCunninghamTheme from '@/cunningham/useCunninghamTheme';

import MenuItem from './MenuItems';
import IconRecent from './assets/icon-clock.svg';
import IconContacts from './assets/icon-contacts.svg';
import IconMail from './assets/icon-mails.svg';
import IconSearch from './assets/icon-search.svg';
import IconFavorite from './assets/icon-stars.svg';

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
        <MenuItem Icon={IconSearch} label={t('Search')} href="/" />
        <MenuItem Icon={IconMail} label={t('Mails')} href="/mails" />
        <MenuItem Icon={IconFavorite} label={t('Favorite')} href="/favorite" />
        <MenuItem Icon={IconRecent} label={t('Recent')} href="/recent" />
        <MenuItem Icon={IconContacts} label={t('Contacts')} href="/contacts" />
        <MenuItem Icon={IconGroup} label={t('Groups')} href="/groups" />
      </Box>
    </Box>
  );
};
