import { Input } from '@openfun/cunningham-react';

interface InputUserEmailProps {
  label: string;
  email: string;
  setEmail: (newEmail: string) => void;
}

export const InputUserEmail = ({
  label,
  email,
  setEmail,
}: InputUserEmailProps) => {
  return (
    <Input
      label={label}
      type="email"
      onChange={(e) => setEmail(e.target.value)}
      required
      fullWidth
      autoComplete="username"
      value={email}
    />
  );
};
