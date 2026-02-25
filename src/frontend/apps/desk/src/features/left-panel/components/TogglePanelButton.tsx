import { Button } from '@gouvfr-lasuite/cunningham-react';
import { useTranslation } from 'react-i18next';

import IconPanelMenu from '@/assets/icons/icon-panel-menu.svg';
import { Icon } from '@/components/';
import { useLeftPanelStore } from '@/features/left-panel';

export const TogglePanelButton = () => {
  const { t } = useTranslation();
  const { isPanelOpen, togglePanel } = useLeftPanelStore();

  return (
    <Button
      size="medium"
      onClick={() => togglePanel()}
      aria-label={isPanelOpen ? t('Close the menu') : t('Open the menu')}
      color="neutral"
      variant="tertiary"
      icon={
        <IconPanelMenu width={24} height={24} aria-hidden />
      }
    />
  );
};
