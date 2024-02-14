import { Button } from '@openfun/cunningham-react';
import React, { CSSProperties } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box, StyledLink } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { TeamsOrdering } from '@/features/teams/api/';
import IconAdd from '@/features/teams/assets/icon-add.svg';
import IconSort from '@/features/teams/assets/icon-sort.svg';
import { useTeamStore } from '@/features/teams/store/useTeamsStore';

const ButtonSort = styled(Button)<{
  $background: CSSProperties['background'];
  $color: CSSProperties['color'];
}>`
  &.c__button {
    svg {
      background-color: transparent;
      transition: all 0.3s;
    }

    &.c__button--active svg {
      background-color: ${({ $background }) => $background};
      border-radius: 10rem;
      color: ${({ $color }) => $color};
    }
  }
`;

export const PanelActions = () => {
  const { t } = useTranslation();
  const { changeOrdering, ordering } = useTeamStore();
  const { colorsTokens } = useCunninghamTheme();

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
      <ButtonSort
        aria-label={t('Sort the teams')}
        icon={
          <IconSort width={30} height={30} aria-label={t('Sort teams icon')} />
        }
        color="tertiary"
        className="c__button-no-bg p-0 m-0"
        onClick={changeOrdering}
        active={ordering === TeamsOrdering.BY_CREATED_ON}
        $background={colorsTokens()['primary-200']}
        $color={colorsTokens()['primary-600']}
      />
      <StyledLink href="/teams/create">
        <Button
          aria-label={t('Add a team')}
          icon={
            <IconAdd width={30} height={30} aria-label={t('Add team icon')} />
          }
          color="tertiary"
          className="c__button-no-bg p-0 m-0"
        />
      </StyledLink>
    </Box>
  );
};
