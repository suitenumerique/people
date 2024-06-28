import Image from 'next/image';
import React, { PropsWithChildren } from 'react';
import { useTranslation } from 'react-i18next';

import { default as IconDevise } from '@/assets/icons/icon-devise.svg?url';
import { default as IconMarianne } from '@/assets/icons/icon-marianne.svg?url';

import { Box } from './Box';
import { Text, TextType } from './Text';

interface LogoGouvProps {
  imagesWidth?: number;
  textProps?: TextType;
}

export const LogoGouv = ({
  imagesWidth,
  children,
  textProps,
}: PropsWithChildren<LogoGouvProps>) => {
  const { t } = useTranslation();

  return (
    <Box>
      <Box>
        <Image
          priority
          src={IconMarianne}
          alt={t('Marianne Logo')}
          width={imagesWidth}
        />
      </Box>
      <Text $weight="bold" {...textProps}>
        {children}
      </Text>
      <Image
        width={imagesWidth}
        priority
        src={IconDevise}
        alt={t('Freedom Equality Fraternity Logo')}
      />
    </Box>
  );
};
