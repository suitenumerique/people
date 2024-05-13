import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, BoxButton } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { EnumMailDomainsOrdering } from '@/features/mail-domains';
import { useMailDomainsStore } from '@/features/mail-domains/store/useMailDomainsStore';

import IconSort from '../../assets/icon-sort.svg';

export const PanelActions = () => {
  const { t } = useTranslation();
  const { changeOrdering, ordering } = useMailDomainsStore();
  const { colorsTokens } = useCunninghamTheme();

  const isSortAsc = ordering === EnumMailDomainsOrdering.BY_CREATED_AT;

  return (
    <Box
      $direction="row"
      $gap="1rem"
      $css={`
        & button {
          padding: 0;

          svg {
            padding: 0.1rem;
          }
        }
      `}
    >
      <BoxButton
        aria-label={
          isSortAsc
            ? t('Sort the domain names by creation date descendent')
            : t('Sort the domain names by creation date ascendent')
        }
        onClick={changeOrdering}
        $radius="100%"
        $background={isSortAsc ? colorsTokens()['primary-200'] : 'transparent'}
        $color={colorsTokens()['primary-600']}
      >
        <IconSort
          width={30}
          height={30}
          aria-label={t('Sort domain names icon')}
        />
      </BoxButton>
    </Box>
  );
};
