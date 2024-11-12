import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group.svg';
import { Box } from '@/components/';
import { useAuthStore } from '@/core/auth';
import useCunninghamTheme from '@/cunningham/useCunninghamTheme';

import MenuItem from './MenuItems';
import IconMailDomains from './assets/icon-mails.svg';

export const Menu = () => {
  const { colorsTokens } = useCunninghamTheme();
  const { userData } = useAuthStore();

  console.log(userData);
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
        {userData?.abilities?.teams.can_view && (
          <MenuItem
            Icon={IconGroup}
            label={t('Teams')}
            href="/teams"
            alias={['/teams']}
          />
        )}
        {userData?.abilities?.mailboxes.can_view && (
          <MenuItem
            Icon={IconMailDomains}
            label={t('Mail Domains')}
            href="/mail-domains"
          />
        )}
      </Box>
    </Box>
  );
};
