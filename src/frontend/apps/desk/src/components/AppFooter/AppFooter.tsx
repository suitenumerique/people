import { Button } from '@gouvfr-lasuite/cunningham-react';
import { LaGaufreV2 } from '@gouvfr-lasuite/ui-kit';
import { QuestionMark } from '@gouvfr-lasuite/ui-kit/icons';
import { useTranslation } from 'react-i18next';

import { useAuthStore } from '@/core/auth';
import { UserInfo } from '@/core/auth/UserInfo';
import { LASUITE_SERVICES_API_URL } from '@/core/lasuite';
import { openSupportWidget } from '@/features/support/openSupportWidget';

export const AppFooter = () => {
  const { t } = useTranslation();
  const { userData } = useAuthStore();

  return (
    <div className="floating-toolbar app-footer">
      <UserInfo />
      <LaGaufreV2 apiUrl={LASUITE_SERVICES_API_URL} />
      <Button
        color="neutral"
        variant="tertiary"
        size="small"
        icon={<QuestionMark />}
        aria-label={t('Contact us')}
        onClick={() => openSupportWidget(userData?.email)}
      />
    </div>
  );
};
