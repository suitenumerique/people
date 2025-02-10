import { useRouter } from 'next/router';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { fetchAPI } from '@/api';
import { LoginForm, LoginLayout } from '@/features/login';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const router = useRouter();
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [blockingError, setBlockingError] = useState('loading');
  const { next } = router.query;

  useEffect(() => {
    if (next) {
      try {
        // Decode the URL-encoded next parameter
        const decodedNext = decodeURIComponent(next as string);
        // Extract the query string after /o/authorize/
        const match = decodedNext.match(/\/o\/authorize\/\?(.*)/);
        if (match) {
          const params = new URLSearchParams(match[1]);
          const acrValues = params.get('acr_values');
          const loginHint = params.get('login_hint');

          if (acrValues && acrValues !== 'eidas1') {
            setBlockingError(t('This authentication level is not supported.'));
          } else {
            setBlockingError('');
          }

          if (loginHint) {
            setEmail(loginHint);
          }
        }
      } catch (e) {
        console.error('Error parsing next parameter:', e);
      }
    }
  }, [next, t]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (blockingError) {
      return;
    }

    fetchAPI('login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      credentials: 'include', // Important for session cookie
    })
      .then((res) => {
        if (!res.ok) {
          setError(t('Login failed. Please try again.'));
        } else {
          if (next) {
            window.location.href = next as string;
          } else {
            window.location.href = '/authorize/';
          }
        }
      })
      .catch(() => {
        setError(t('Login failed. Please try again.'));
      });
  };

  return (
    <LoginForm
      title={t('Sign in')}
      labelEmail={t('Email')}
      labelPassword={t('Password')}
      labelSignIn={t('Sign in')}
      email={email}
      setEmail={setEmail}
      setPassword={setPassword}
      error={error}
      handleSubmit={handleSubmit}
      blockingError={blockingError}
    />
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <LoginLayout>{page}</LoginLayout>;
};

export default Page;
