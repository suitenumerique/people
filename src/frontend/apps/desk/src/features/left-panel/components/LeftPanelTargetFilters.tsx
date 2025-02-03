import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { css } from 'styled-components';

import { SeparatedSection } from '@/components/separators';

import { Box, BoxButton, Icon, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { useLeftPanelStore } from '@/features/left-panel';

export const LeftPanelTargetFilters = () => {
  const { t } = useTranslation();
  const { closePanel } = useLeftPanelStore();
  const { colorsTokens, spacingsTokens } = useCunninghamTheme();
  const spacing = spacingsTokens();
  const colors = colorsTokens();

  const searchParams = useSearchParams();

  const router = useRouter();
  const pathname = usePathname();

  const defaultQueries = useMemo(() => {
    return [
      {
        icon: 'group',
        label: t('Groups'),
        targetQuery: '/teams',
      },
      {
        icon: 'mail',
        label: t('Mail Domains'),
        targetQuery: '/mail-domains',
      },
    ];
  }, [t]);

  const onSelectQuery = (query: String) => {
    router.push(query);
    closePanel();
  };

  return (
    <Box
      $justify="center"
      $gap={spacing['2xs']}
    >
      {defaultQueries.map((query, index) => {
       const isActive = pathname === query.targetQuery ||
        pathname.startsWith(`${query.targetQuery}/`);

        return (
          <SeparatedSection 
            key={query.icon}
            showSeparator={defaultQueries.length - 1 > index}
            $padding={{ horizontal: 'l' }}
          >
            <BoxButton
              aria-label={query.label}
              onClick={() => onSelectQuery(query.targetQuery)}
              $direction="row"
              $margin="10px"
              aria-selected={isActive}
              $align="center"
              $justify="flex-start"
              $gap={spacing['xs']}
              $radius={spacing['3xs']}
              $padding={{ all: '2xs' }}
              $css={css`
                cursor: pointer;
                background-color: ${isActive
                  ? colors['greyscale-100']
                  : undefined};
                font-weight: ${isActive ? 700 : undefined};
                &:hover {
                  background-color: ${colors['greyscale-100']};
                }
              `}
            >
              <Icon
                $variation={isActive ? '1000' : '700'}
                iconName={query.icon}
              />
              <Text $variation={isActive ? '1000' : '700'} $size="sm">
                {query.label}
              </Text>
            </BoxButton>
          </SeparatedSection>
        );
      })}
    </Box>
  );
};