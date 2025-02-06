import { useCunninghamTheme } from '@/cunningham';
import { Box } from '@/components';
import { Tooltip } from "@openfun/cunningham-react";
import { useTranslation } from 'react-i18next';

const TagContent = ({
  ...props
}) => {
  const { colorsTokens } = useCunninghamTheme();
  const { t } = useTranslation();

  const textColor = {
    'pending': colorsTokens()['info-600'],
    'enabled': colorsTokens()['success-600'],
    'disabled': colorsTokens()['greyscale-600'],
    'failed': colorsTokens()['warning-600']
  }

  const backgroundColor = {
    'pending': colorsTokens()['info-100'],
    'enabled': colorsTokens()['success-600'],
    'disabled': colorsTokens()['greyscale-100'],
    'failed': colorsTokens()['warning-100']
  }

  return (
    <Box
      $background={backgroundColor[props.status]}
      $color={textColor[props.status]}
      $radius="4px"
      $css={`
        padding: 4px 8px;
        font-weight: 700;
        cursor: default;
      `}
    >
      {t(props.status)}
    </Box>
  );
};

export const Tag = ({
  ...props
}) => {
  return props.tooltip ? (
    <Tooltip content={props.tooltip} placement="top">
      <Box>
        <TagContent {...props} />
      </Box>
    </Tooltip>
  ) : (
    <TagContent {...props} />
  );
};