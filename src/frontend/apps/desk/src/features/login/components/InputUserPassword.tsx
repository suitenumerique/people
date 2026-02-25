import { Input } from '@gouvfr-lasuite/cunningham-react';

interface InputUserEmailProps {
  label: string;
  setPassword: (newEmail: string) => void;
}

export const InputUserPassword = ({
  label,
  setPassword,
}: InputUserEmailProps) => {
  return (
    <Input
      label={label}
      type="password"
      onChange={(e) => setPassword(e.target.value)}
      required
      fullWidth
      autoComplete="current-password"
    />
  );
};
