import { Button } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';

import { useAuthStore } from '@/core/auth';

export const ButtonLogin = () => {
  const { t } = useTranslation();
  const { logout } = useAuthStore();

  return (
    <Button onClick={logout} color="primary-text" aria-label={t('Logout')}>
      {t('Logout')}
    </Button>
  );
};
