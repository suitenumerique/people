import { Button } from '@gouvfr-lasuite/cunningham-react';
import { UserMenu } from '@gouvfr-lasuite/ui-kit';
import { useTranslation } from 'react-i18next';

import { baseApiUrl } from '@/api';
import { useAuthStore } from '@/core/auth';
import { LanguagePicker } from '@/features/language';

interface UserMenuUser {
  email: string;
  full_name: string;
  organization?: string;
}

export const UserInfo = () => {
  const { t } = useTranslation();
  const { authenticated, userData, logout } = useAuthStore();
  const user: UserMenuUser = {
    email: userData?.email ?? '',
    full_name: userData?.name ?? '',
    organization:
      typeof userData?.organization === 'string'
        ? userData.organization
        : (userData?.organization?.name ?? ''),
  };

  if (!authenticated) {
    return null;
  }

  if (!userData) {
    return (
      <Button
        color="brand"
        variant="tertiary"
        onClick={() =>
          window.location.assign(new URL('authenticate/', baseApiUrl()).href)
        }
      >
        {t('Sign in')}
      </Button>
    );
  }

  return <UserMenu user={user} logout={logout} actions={<LanguagePicker />} />;
};
