import React, { InputHTMLAttributes } from 'react';

import { Box, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

export const Input = ({ label, error, required, ...props }: InputProps) => {
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Box>
      <Box $display="flex" $gap="8px" $margin={{ bottom: 'sm' }}>
        <label
          htmlFor={label}
          style={{ fontWeight: 500, color: colorsTokens()['gray-900'] }}
        >
          {label} {required && '*'}
        </label>
        <input
          id={label}
          aria-required={required}
          required={required}
          style={{
            padding: '12px',
            borderRadius: '4px',
            fontSize: '14px',
            border: `1px solid ${error ? colorsTokens()['error-500'] : 'var(--c--contextuals--border--semantic--neutral--tertiary)'}`,
            background: colorsTokens()['gray-000'],
            color: colorsTokens()['gray-550'],
          }}
          {...props}
        />
      </Box>
      {error && (
        <Text $size="xs" $theme="error" $variation="secondary">
          {error}
        </Text>
      )}
    </Box>
  );
};
