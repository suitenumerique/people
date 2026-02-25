import clsx from 'clsx';
import { css } from 'styled-components';

import { Text, TextType } from '@/components';

type IconProps = TextType & {
  iconName: string;
};
export const Icon = ({
  iconName,
  ...textProps
}: IconProps) => {
  return (
    <Text
      {...textProps}
      aria-hidden="true"
      className={clsx('material-icons', textProps.className)}
    >
      {iconName}
    </Text>
  );
};

type IconOptionsProps = TextType & {
  isHorizontal?: boolean;
};

export const IconOptions = ({ isHorizontal, ...props }: IconOptionsProps) => {
  return (
    <Icon
      {...props}
      aria-hidden="true"
      iconName={isHorizontal ? 'more_horiz' : 'more_vert'}
      $css={css`
        color: var(--c--contextuals--content--semantic--brand--tertiary);
        user-select: none;
        ${props.$css}
      `}
    />
  );
};
