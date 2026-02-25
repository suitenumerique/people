import React from 'react';

import { Box, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

export type LocalInputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  right: React.ReactNode;
  error?: string;
  required?: boolean;
  id: string;
};

export const LocalInput = ({
  label,
  right,
  error,
  required,
  id,
  ...inputProps
}: LocalInputProps) => {
  const { colorsTokens } = useCunninghamTheme();
  const borderColor = error
    ? colorsTokens()['error-500']
    : 'var(--c--contextuals--border--semantic--neutral--tertiary)';

  return (
    <Box>
      <Box $margin={{ bottom: 'sm' }}>
        <label
          htmlFor={id}
          style={{ fontWeight: 500, color: colorsTokens()['gray-900'] }}
        >
          {label} {required && '*'}
        </label>
      </Box>
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          flexWrap: 'nowrap',
          alignItems: 'stretch',
          border: `1px solid ${borderColor}`,
          borderRadius: 4,
          overflow: 'hidden',
          background: colorsTokens()['gray-000'],
        }}
      >
        <input
          id={id}
          aria-required={required}
          required={required}
          style={{
            flex: '1 1 0',
            minWidth: 0,
            padding: '12px',
            border: 'none',
            borderRadius: 0,
            fontSize: 14,
            background: 'transparent',
            color: colorsTokens()['gray-550'],
            outline: 'none',
          }}
          {...inputProps}
        />
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            flexShrink: 0,
            background: 'transparent',
          }}
        >
          {right}
        </div>
      </div>
      {error && (
        <Text
          $size="xs"
          $theme="error"
          $variation="secondary"
          $margin={{ top: '2xs' }}
        >
          {error}
        </Text>
      )}
    </Box>
  );
};
