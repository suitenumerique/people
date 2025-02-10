import { Button } from '@openfun/cunningham-react';

import { Box, Text } from '@/components';
import { InputUserEmail, InputUserPassword } from '@/features/login';

interface LoginFormProps {
  title: string;
  labelEmail: string;
  labelPassword: string;
  labelSignIn: string;
  email: string;
  setEmail: (newEmail: string) => void;
  setPassword: (newPassword: string) => void;
  error: string;
  handleSubmit: (e: React.FormEvent) => void;
  blockingError: string;
}

export const LoginForm = ({
  title,
  labelEmail,
  labelPassword,
  labelSignIn,
  email,
  setEmail,
  setPassword,
  error,
  handleSubmit,
  blockingError,
}: LoginFormProps) => {
  return (
    <Box $width="100%" $maxWidth="30rem" $margin="4rem auto" $padding="0 1rem">
      <Box>
        <Text
          as="h1"
          $textAlign="center"
          $size="h3"
          $theme="primary"
          $variation="text"
          style={{ marginBottom: '2rem' }}
        >
          {title}
        </Text>
        <Box>
          {!!blockingError ? (
            <Text
              $theme="danger"
              $variation="text"
              $textAlign="center"
              style={{ marginBottom: '1rem', display: 'block' }}
            >
              {blockingError === 'loading' ? '' : blockingError}
            </Text>
          ) : (
            <form onSubmit={handleSubmit} data-testId="login-form">
              <Box $padding="tiny">
                <InputUserEmail
                  setEmail={setEmail}
                  email={email}
                  label={labelEmail}
                />
              </Box>

              <Box $padding="tiny">
                <InputUserPassword
                  label={labelPassword}
                  setPassword={setPassword}
                />
              </Box>

              {error && (
                <Box $padding="tiny">
                  <Text
                    $theme="danger"
                    $variation="text"
                    $textAlign="center"
                    style={{ marginBottom: '1rem', display: 'block' }}
                  >
                    {error}
                  </Text>
                </Box>
              )}

              <Box $padding="tiny">
                <Button color="primary" type="submit" fullWidth>
                  {labelSignIn}
                </Button>
              </Box>
            </form>
          )}
        </Box>{' '}
      </Box>
    </Box>
  );
};
