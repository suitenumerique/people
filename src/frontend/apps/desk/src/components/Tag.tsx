import { Tooltip } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';

import { Box } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

interface TagContentProps {
  status: 'pending' | 'enabled' | 'disabled' | 'failed' | 'action_required';
  showTooltip?: boolean;
  tooltipType?: 'domain' | 'mail';
  placement?: 'top' | 'bottom';
}

const TagContent = ({ status }: TagContentProps) => {
  const { colorsTokens } = useCunninghamTheme();
  const { t } = useTranslation();

  const textColor = {
    pending: colorsTokens()['info-600'],
    enabled: colorsTokens()['success-600'],
    disabled: colorsTokens()['greyscale-600'],
    action_required: colorsTokens()['warning-600'],
    failed: colorsTokens()['danger-600'],
  };

  const backgroundColor = {
    pending: colorsTokens()['info-100'],
    enabled: colorsTokens()['success-100'],
    disabled: colorsTokens()['greyscale-100'],
    action_required: colorsTokens()['warning-100'],
    failed: colorsTokens()['danger-100'],
  };

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
      {t(status).replace('_', ' ')}
    </Box>
  );
};

export const Tag = ({ ...props }: TagContentProps) => {
  const { t } = useTranslation();

  const tooltipText: Record<
    NonNullable<TagContentProps['tooltipType']>,
    Partial<Record<TagContentProps['status'], string>>
  > = {
    domain: {
      pending: 'Domain pending validation by an administrator',
      enabled: 'Active domain',
      disabled: 'Disabled domain',
      failed: 'Domain error, contact an administrator',
      action_required:
        'A configuration action from the domain manager (outside Régie) is required',
    },
    mail: {
      pending: 'Email address pending validation by an administrator',
      enabled: 'Functional email address',
      failed: 'Email address error, contact an administrator',
      disabled: 'Disabled email address',
    },
  };

  const rawTooltip =
    props.tooltipType && tooltipText[props.tooltipType]?.[props.status];

  const tooltipContent = rawTooltip ? t(rawTooltip) : '';

  return props.showTooltip ? (
    <Tooltip content={tooltipContent} placement={props.placement || 'top'}>
      <Box>
        <TagContent status={props.status} />
      </Box>
    </Tooltip>
  ) : (
    <TagContent status={props.status} />
  );
};
