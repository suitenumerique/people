import { Button } from '@openfun/cunningham-react';
import Image from 'next/image';
import { useTranslation } from 'react-i18next';

import { default as IconRegie } from '@/assets/logo-regie.svg?url';
import { Icon, StyledLink, Text } from '@/components/';
import { ButtonLogin } from '@/core/auth';
import { useCunninghamTheme } from '@/cunningham';
import { LanguagePicker } from '@/features/language';
import { useLeftPanelStore } from '@/features/left-panel';

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
      style={{
        display: 'flex',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 'var(--header-height)',
        minHeight: 'var(--header-height)',
        padding: `0 ${spacings['base']}`,
        backgroundColor: colors['greyscale-000'],
        borderBottom: `1px solid ${colors['greyscale-200']}`,
      }}
    >
      <Button
        className="md:hidden"
        size="medium"
        onClick={() => togglePanel()}
        aria-label={t('Open the header menu')}
        color="tertiary-text"
        icon={
          <Icon
            $variation="800"
            $theme="primary"
            iconName={isPanelOpen ? 'close' : 'menu'}
          />
        }
      />
      <StyledLink href="/">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacings['3xs'],
          }}
        >
          <Image priority src={IconRegie} alt={t('La régie Logo')} width={25} />
          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              gap: spacings['xs'],
            }}
          >
            <Text
              as="h2"
              style={{ color: '#000091', zIndex: 1, fontSize: '1.30rem' }}
            >
              {t('La Régie')}
            </Text>
            <Text
              style={{
                padding: '1px 8px',
                fontSize: '11px',
                fontWeight: 'bold',
                color: colors['primary-500'],
                borderRadius: '12px',
                backgroundColor: colors['primary-200'],
              }}
            >
              BETA
            </Text>
          </div>
        </div>
      </StyledLink>
      <div className="md:hidden">
        <div
          style={{ display: 'flex', flexDirection: 'row', gap: spacings['sm'] }}
        >
          <LaGaufre />
        </div>
      </div>
      <div className="hidden md:block">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacings['sm'],
            flexDirection: 'row',
          }}
        >
          <ButtonLogin />
          <LanguagePicker />
          <LaGaufre />
        </div>
      </div>
    </header>
  );
};
