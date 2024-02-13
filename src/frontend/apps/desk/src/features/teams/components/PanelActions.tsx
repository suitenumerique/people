import { Button } from '@openfun/cunningham-react';
import Image from 'next/image';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box } from '@/components';

import { default as IconAdd } from '../assets/icon-add.svg?url';
import { default as IconSort } from '../assets/icon-sort.svg?url';

export const PanelActions = () => {
  const { t } = useTranslation();

  return (
    <Box
      $direction="row"
      $gap="1rem"
      $css={`
        & > button {
          padding: 0;
        }
      `}
    >
      <Button
        aria-label={t('Sort the teams')}
        icon={<Image priority src={IconSort} alt={t('Sort teams icon')} />}
        color="tertiary"
        className="c__button-no-bg p-0 m-0"
      />
      <Button
        aria-label={t('Add a team')}
        icon={<Image priority src={IconAdd} alt={t('Add team icon')} />}
        color="tertiary"
        className="c__button-no-bg p-0 m-0"
      />
    </Box>
  );
};
