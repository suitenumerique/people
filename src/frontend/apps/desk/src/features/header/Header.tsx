import { Button } from '@gouvfr-lasuite/cunningham-react';
import Image from 'next/image';
import { useTranslation } from 'react-i18next';

import { default as IconRegie } from '@/assets/logo-regie.svg?url';
import { Icon, StyledLink, Text } from '@/components/';
import { UserInfo } from '@/core/auth/UserInfo';
import { useCunninghamTheme } from '@/cunningham';
import { useLeftPanelStore } from '@/features/left-panel';
import { TogglePanelButton } from '@/features/left-panel/components/TogglePanelButton';

import { LaGaufre } from './LaGaufre';
export const HEADER_HEIGHT = '52px';

export const Header = () => {
  const { t } = useTranslation();
  const theme = useCunninghamTheme();
  const { isPanelOpen, togglePanel } = useLeftPanelStore();

  const spacings = theme.spacingsTokens();
  const colors = theme.colorsTokens();

  return (
    <header
    className="container"
      style={{
        display: 'flex',
        top: '0px',
        left: 0,
        right: 0,
        zIndex: 1000,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 'var(--header-height)',
        minHeight: 'var(--header-height)',
      }}
    >
      <Button
        className="md:hidden"
        size="medium"
        onClick={() => togglePanel()}
        aria-label={t('Open the header menu')}
        color="neutral"
        variant="tertiary"
        icon={
          <Icon
            $variation="800"
            $theme="primary"
            iconName={isPanelOpen ? 'close' : 'menu'}
          />
        }
      />
      <div
          style={{
            display: 'flex',
            alignItems: 'center',
            borderRadius: '8px',
            backgroundColor: 'var(--c--contextuals--background--surface--primary)',
            backdropFilter: 'blur(10px)',
            border: '1px solid var(--c--contextuals--border--surface--primary)',
            padding: '4px',
            flexDirection: 'row',
            boxShadow: '0 2px 4px 0 rgba(0, 0, 0, 0.05)',
          }}
        >
          <TogglePanelButton />
          <div
            style={{
              overflow: 'hidden',
              maxWidth: isPanelOpen ? 0 : 120,
              opacity: isPanelOpen ? 0 : 1,
              transition: 'max-width 0.3s ease, opacity 0.2s ease 0.3s',
            }}
          >
            <StyledLink href="/">
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <Image priority src={IconRegie} alt="Régie Logo" height={34} />
              </div>
            </StyledLink>
          </div>
      </div>
{/*      <div className="md:hidden">
        <div
          style={{ display: 'flex', flexDirection: 'row', gap: spacings['sm'] }}
        >
          <LaGaufre />
        </div>
      </div>*/}
      <div className="">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            borderRadius: '8px',
            backgroundColor: 'var(--c--contextuals--background--surface--primary)',
            border: '1px solid var(--c--contextuals--border--surface--primary)',
            padding: '4px',
            gap: '4px',
            flexDirection: 'row',
            boxShadow: '0 2px 4px 0 rgba(0, 0, 0, 0.05)',
          }}
        >
          <UserInfo />
          <LaGaufre />
        </div>
      </div>
    </header>
  );
};
