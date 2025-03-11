import { useCunninghamTheme } from '@/cunningham';
import { Box } from '@/components';
import { Tooltip } from "@openfun/cunningham-react";
import { useTranslation } from 'react-i18next';

interface TagContentProps {
  status: 'pending' | 'enabled' | 'disabled' | 'failed';
  tooltip?: string;
}

const TagContent = ({ status }: TagContentProps) => {
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
    'enabled': colorsTokens()['success-100'],
    'disabled': colorsTokens()['greyscale-100'],
    'failed': colorsTokens()['warning-100']
  }

  return (
    <Box
      $background={backgroundColor[status]}
      $color={textColor[status]}
      $radius="4px"
      $css={`
        padding: 4px 8px;
        font-weight: 600;
        cursor: default;
        text-transform: capitalize;
      `}
    >
      {t(status)}
    </Box>
  );
};

export const Tag = ({
  ...props
}) => {
  return props.tooltip ? (
    <Tooltip content={props.tooltip} placement="top">
      <Box>
        <TagContent status={props.status} />
      </Box>
    </Tooltip>
  ) : (
    <TagContent status={props.status} />
  );
};