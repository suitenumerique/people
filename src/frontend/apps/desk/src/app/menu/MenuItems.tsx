import { Button } from '@openfun/cunningham-react';
import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box } from '@/components/';
import { useCunninghamTheme } from '@/cunningham';
import { SVGComponent } from '@/types/components';

import { Tooltip } from './Tooltip';

interface MenuItemProps {
  Icon: SVGComponent;
  label: string;
}

const MenuItem = ({ Icon, label }: MenuItemProps) => {
  const { t } = useTranslation();
  const buttonRef = useRef(null);
  const { colorsTokens } = useCunninghamTheme();
  const [isTooltipOpen, setIsTooltipOpen] = useState(false);

  return (
    <>
      <Box
        className="m-st p-t"
        as="li"
        $justify="center"
        ref={buttonRef}
        $css={`
          & > button { padding: 0};
          transition: all 0.2s ease-in-out
        `}
        $background={colorsTokens()['primary-300']}
        $radius="10px"
        onMouseOver={() => setIsTooltipOpen(true)}
        onMouseOut={() => setIsTooltipOpen(false)}
      >
        <Button
          aria-label={t(`{{label}} button`, { label })}
          icon={
            <Box $color={colorsTokens()['primary-600']}>
              <Icon
                width="2.375rem"
                aria-label={t(`{{label}} icon`, { label })}
                color="#ffffff"
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
          buttonRef={buttonRef}
          label={label}
          backgroundColor="#ffffff"
          textColor="#000000"
        />
      )}
    </>
  );
};

export default MenuItem;
