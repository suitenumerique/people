import { useTranslation } from 'react-i18next';
import { UserMenu } from '@gouvfr-lasuite/ui-kit';
import { Button } from '@gouvfr-lasuite/cunningham-react';
import { LanguagePicker } from '@/features/language';
import { baseApiUrl } from '@/api';
import { useAuthStore } from '@/core/auth';

interface UserMenuUser {
  email: string;
  full_name: string;
  organization: string;
}

export const UserInfo = () => {
  const { t } = useTranslation();
  const { authenticated, userData, logout } = useAuthStore();
  const user: UserMenuUser = {
    email: userData?.email,
    full_name: userData?.name,
    organization: userData?.organization,
  }

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

  return (
    <UserMenu
      user={user}
      logout={logout}
      actions={<LanguagePicker />}
      termOfServiceUrl="https://docs.numerique.gouv.fr/docs/8e298e03-c95f-44c7-be4a-ffb618af1854/"
    />
  );
};