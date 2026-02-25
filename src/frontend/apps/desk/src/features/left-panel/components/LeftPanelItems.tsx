import { Button } from '@gouvfr-lasuite/cunningham-react';
import { usePathname, useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import { Icon, Text } from '@/components';
import { SeparatedSection } from '@/components/separators';
import { useAuthStore } from '@/core/auth';
import { useLeftPanelStore } from '@/features/left-panel';

export const LeftPanelItems = () => {
  const { t } = useTranslation();
  const { closePanel } = useLeftPanelStore();
  const { userData } = useAuthStore();

  const router = useRouter();
  const pathname = usePathname();

  const defaultQueries = [
    {
      icon: 'group',
      label: t('Groups'),
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
    if (typeof window !== 'undefined' && !window.matchMedia('(min-width: 768px)').matches) {
      closePanel();
    }
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
            <Button
              color="neutral"
              variant="tertiary"
              style={{backgroundColor: isActive ? 'var(--c--contextuals--background--semantic--overlay--primary)' : '', fontWeight: isActive ? 'bold' : '500', marginBottom: '4px'}}
              key={query.label}
              data-testid={`${query.label} button`}
              aria-label={`${query.label} button`}
              aria-current={isActive ? 'page' : undefined}
              onClick={() => onSelectQuery(query.targetQuery)}
              icon={<Icon width="16" height="16" $theme="neutral" iconName={query.icon} />}
            >
              <Text $size="sm">
                {query.label}
              </Text>
            </Button>
        );
      })}
    </div>
  );
};
