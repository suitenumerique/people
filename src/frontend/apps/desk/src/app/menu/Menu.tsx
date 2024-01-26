import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box } from '@/components/';
import useCunninghamTheme from '@/cunningham/useCunninghamTheme';

import MenuItem from './MenuItems';
import IconRecent from './assets/icon-clock.svg';
import IconContacts from './assets/icon-contacts.svg';
import IconGroup from './assets/icon-group.svg';
import IconSearch from './assets/icon-search.svg';
import IconFavorite from './assets/icon-stars.svg';

export const Menu = () => {
  const { colorsTokens } = useCunninghamTheme();
  const { t } = useTranslation();

  return (
    <Box
      as="menu"
      className="m-0 p-0"
      $background={colorsTokens()['primary-800']}
      $height="100%"
      $width="3.75rem"
      $justify="space-between"
      $direction="column"
    >
      <Box $direction="column">
        <MenuItem Icon={IconSearch} label={t('Search')} />
        <MenuItem Icon={IconFavorite} label={t('Favorite')} />
        <MenuItem Icon={IconRecent} label={t('Recent')} />
        <MenuItem Icon={IconContacts} label={t('Contacts')} />
        <MenuItem Icon={IconGroup} label={t('Groups')} />
      </Box>
    </Box>
  );
};
