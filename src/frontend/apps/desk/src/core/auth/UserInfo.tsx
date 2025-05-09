import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { useAuthStore } from '@/core/auth';

export const UserInfo = () => {
  const { t } = useTranslation();
  const { authenticated, userData } = useAuthStore();
  const userName = userData?.name || userData?.email || t('No Username');
  const organizationName = userData?.organization?.name || '';

  return authenticated ? (
    <Box $direction="column" $align="left">
      <Text $theme="primary">
        {userName}
        {organizationName ? ` | ${organizationName}` : ''}
      </Text>
    </Box>
  ) : null;
};
