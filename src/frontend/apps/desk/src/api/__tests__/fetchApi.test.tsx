import fetchMock from 'fetch-mock';

import { fetchAPI } from '@/api';
import { useAuthStore } from '@/core/auth';

describe('fetchAPI', () => {
  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = 'http://some.api.url/api/v1.0/';
    fetchMock.restore();
  });

  it('adds correctly the basename', () => {
    fetchMock.mock('http://some.api.url/api/v1.0/some/url', 200);

    void fetchAPI('some/url');

    expect(fetchMock.lastUrl()).toEqual(
      'http://some.api.url/api/v1.0/some/url',
    );
  });

  it('adds the credentials automatically', () => {
    fetchMock.mock('http://some.api.url/api/v1.0/some/url', 200);

    void fetchAPI('some/url', { body: 'some body' });

    expect(fetchMock.lastOptions()).toEqual({
      body: 'some body',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  it('logout if 401 response', async () => {
    useAuthStore.setState({
      authenticated: true,
      userData: { id: '123', email: 'test@test.com' },
    });

    fetchMock.mock('http://some.api.url/api/v1.0/some/url', 401);
    fetchMock.mock('http://some.api.url/api/v1.0/logout/', 302);

    await fetchAPI('some/url');

    await Promise.all([fetchMock.flush()]);

    expect(fetchMock.lastUrl()).toEqual('http://some.api.url/api/v1.0/logout/');

    const { userData, authenticated } = useAuthStore.getState();
    expect(userData).toBeUndefined();
    expect(authenticated).toBeFalsy();
  });
});
