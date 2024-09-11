import { usePathname, useRouter } from 'next/navigation';
import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, BoxButton } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { SVGComponent } from '@/types/components';

import { Tooltip } from './Tooltip';

interface MenuItemProps {
  Icon: SVGComponent;
  label: string;
  href: string;
  alias?: string[];
}

const MenuItem = ({ Icon, label, href, alias }: MenuItemProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const pathname = usePathname();
  const { colorsTokens } = useCunninghamTheme();
  const parentRef = useRef(null);
  const [isTooltipOpen, setIsTooltipOpen] = useState(false);

  const isActive =
    pathname === href ||
    alias?.includes(pathname) ||
    pathname.startsWith(`${href}/`) ||
    alias?.some((a) => pathname.startsWith(`${a}/`));

  const { color, background, colorTooltip, backgroundTooltip } = isActive
    ? {
        color: colorsTokens()['primary-600'],
        background: colorsTokens()['primary-300'],
        backgroundTooltip: 'white',
        colorTooltip: 'black',
      }
    : {
        color: '#ffffff55',
        background: undefined,
        backgroundTooltip: '#161616',
        colorTooltip: 'white',
      };

  return (
    <Box ref={parentRef}>
      <Box
        $margin="xtiny"
        $padding="tiny"
        as="li"
        $justify="center"
        $css="transition: all 0.2s ease-in-out;"
        $background={background}
        $radius="10px"
      >
        <BoxButton
          aria-current={isActive && 'page'}
          onMouseOver={() => setIsTooltipOpen(true)}
          onMouseLeave={() => setIsTooltipOpen(false)}
          $css={`
            padding: 0;
            ${isActive ? null : '&:focus-visible {outline: #fff solid 2px;}'}
        `}
          aria-label={t(`{{label}} button`, { label })}
          $color={color}
          as="button"
          onClick={() => router.push(href)}
        >
          <Icon
            width="2.375rem"
            aria-hidden="true"
            style={{
              transition: 'color 0.2s ease-in-out',
            }}
          />
        </BoxButton>
      </Box>
      <Box as="span">
        {isTooltipOpen && (
          <Tooltip
            parentRef={parentRef}
            label={label}
            backgroundColor={backgroundTooltip}
            textColor={colorTooltip}
          />
        )}
      </Box>
    </Box>
  );
};

export default MenuItem;
