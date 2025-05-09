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
        style={{ fontWeight: 500, color: colorsTokens()['greyscale-900'] }}
      >
        {label} {required && '*'}
      </label>
      <input
        id={label}
        aria-required={required}
        required={required}
        style={{
          padding: '12px',
          margin: '6px 0',
          borderRadius: '4px',
          fontSize: '14px',
          border: `1px solid ${error ? colorsTokens()['danger-500'] : colorsTokens()['greyscale-400']}`,
          background: colorsTokens()['greyscale-050'],
          color: colorsTokens()['greyscale-900'],
        }}
        {...props}
      />
      {error && (
        <Text $size="xs" $color="error-500">
          {error}
        </Text>
      )}
    </Box>
  );
};
