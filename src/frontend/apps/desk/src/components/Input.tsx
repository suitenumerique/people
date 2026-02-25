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
    <Box $display="flex" $gap="4px">
      <label
        htmlFor={label}
        style={{ fontWeight: 500, color: colorsTokens()['gray-900'] }}
      >
        {label} {required && '*'}
      </label>
      {error && (
        <Text $size="xs" $theme="danger" $variation="600">
          {error}
        </Text>
      )}
      <input
        id={label}
        aria-required={required}
        required={required}
        style={{
          padding: '12px',
          borderRadius: '4px',
          fontSize: '14px',
          border: `1px solid ${error ? colorsTokens()['error-500'] : colorsTokens()['gray-400']}`,
          background: colorsTokens()['gray-050'],
          color: colorsTokens()['gray-900'],
        }}
        {...props}
      />
    </Box>
  );
};
