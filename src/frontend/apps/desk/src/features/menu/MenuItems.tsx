import { Button } from '@openfun/cunningham-react';
import { usePathname } from 'next/navigation';
import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, StyledLink } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { SVGComponent } from '@/types/components';

import { Tooltip } from './Tooltip';

interface MenuItemProps {
  Icon: SVGComponent;
  label: string;
  href: string;
}

const MenuItem = ({ Icon, label, href }: MenuItemProps) => {
  const { t } = useTranslation();
  const pathname = usePathname();
  const { colorsTokens } = useCunninghamTheme();
  const parentRef = useRef(null);
  const [isTooltipOpen, setIsTooltipOpen] = useState(false);

  const isActive = pathname === href;
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
    <StyledLink
      href={href}
      aria-current={isActive && 'page'}
      ref={parentRef}
      onMouseOver={() => setIsTooltipOpen(true)}
      onMouseOut={() => setIsTooltipOpen(false)}
      style={{ display: 'block' }}
    >
      <Box
        className="m-st p-t"
        as="li"
        $justify="center"
        $css={`
          & > button { padding: 0};
          transition: all 0.2s ease-in-out
        `}
        $background={background}
        $radius="10px"
      >
        <Button
          aria-label={t(`{{label}} button`, { label })}
          icon={
            <Box $color={color}>
              <Icon
                width="2.375rem"
                aria-label={t(`{{label}} icon`, { label })}
                style={{
                  transition: 'color 0.2s ease-in-out',
                }}
              />
            </Box>
          }
          color="tertiary"
          className="c__button-no-bg p-0 m-0"
          style={{ flexDirection: 'column', gap: '0' }}
        />
      </Box>
      {isTooltipOpen && (
        <Tooltip
          parentRef={parentRef}
          label={label}
          backgroundColor={backgroundTooltip}
          textColor={colorTooltip}
        />
      )}
    </StyledLink>
  );
};

export default MenuItem;
