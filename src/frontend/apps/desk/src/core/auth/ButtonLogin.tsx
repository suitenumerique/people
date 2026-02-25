import { Button } from '@gouvfr-lasuite/cunningham-react';
import { useTranslation } from 'react-i18next';

import { useAuthStore } from '@/core/auth';

export const ButtonLogin = () => {
  const { t } = useTranslation();
  const { logout } = useAuthStore();

  return (
    <Button
      onClick={logout}
      color="brand"
      variant="tertiary"
      aria-label={t('Logout')}
    >
      {t('Logout')}
    </Button>
  );
};
