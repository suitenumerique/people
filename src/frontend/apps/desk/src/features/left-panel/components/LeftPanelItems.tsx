import { Button } from '@openfun/cunningham-react';
import { usePathname, useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import { Icon, Text } from '@/components';
import { SeparatedSection } from '@/components/separators';
import { useAuthStore } from '@/core/auth';
import { useCunninghamTheme } from '@/cunningham';
import { useLeftPanelStore } from '@/features/left-panel';

export const LeftPanelItems = () => {
  const { t } = useTranslation();
  const { closePanel } = useLeftPanelStore();
  const { colorsTokens } = useCunninghamTheme();
  const { userData } = useAuthStore();

  const colors = colorsTokens();

  const router = useRouter();
  const pathname = usePathname();

  const defaultQueries = [
    {
      icon: 'group',
      label: t('Teams'),
      targetQuery: '/teams',
      abilities: userData?.abilities?.teams.can_view,
    },
    {
      icon: 'mail',
      label: t('Mail Domains'),
      targetQuery: '/mail-domains',
      abilities: userData?.abilities?.mailboxes.can_view,
    },
  ];

  const onSelectQuery = (query: string) => {
    router.push(query);
    closePanel();
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--c--theme--spacings--2xs)',
      }}
    >
      {defaultQueries.map((query, index) => {
        if (!query.abilities) {
          return null;
        }

        const isActive =
          pathname === query.targetQuery ||
          pathname.startsWith(`${query.targetQuery}/`);

        return (
          <SeparatedSection
            key={query.label}
            showSeparator={defaultQueries.length - 1 > index}
          >
            <Button
              data-testid={`${query.label} button`}
              aria-label={`${query.label} button`}
              onClick={() => onSelectQuery(query.targetQuery)}
              style={{
                gap: 'var(--c--theme--spacings--xs)',
                margin: '10px 0',
                cursor: 'pointer',
                border: 'none',
                backgroundColor: isActive
                  ? colors['greyscale-100']
                  : colors['greyscale-000'],
                fontWeight: isActive ? 700 : undefined,
              }}
            >
              <Icon
                $variation={isActive ? '1000' : '700'}
                iconName={query.icon}
              />
              <Text $variation={isActive ? '1000' : '700'} $size="sm">
                {query.label}
              </Text>
            </Button>
          </SeparatedSection>
        );
      })}
    </div>
  );
};
