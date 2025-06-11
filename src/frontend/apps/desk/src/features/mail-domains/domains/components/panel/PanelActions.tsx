import React from 'react';
import { useTranslation } from 'react-i18next';

import IconAdd from '@/assets/icons/icon-add.svg';
import IconSort from '@/assets/icons/icon-sort.svg';
import { Box, BoxButton, StyledLink, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import {
  EnumMailDomainsOrdering,
  useMailDomainsStore,
} from '@/features/mail-domains/domains';

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
          justify-content: start;

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
        <IconSort width={30} height={30} aria-hidden="true" />
      </BoxButton>

      <StyledLink href="/mail-domains/add/">
        <Text
          $margin="auto"
          aria-label={t('Add a mail domain')}
          $theme="primary"
        >
          <IconAdd width={27} height={27} aria-hidden="true" />
        </Text>
      </StyledLink>
    </Box>
  );
};
