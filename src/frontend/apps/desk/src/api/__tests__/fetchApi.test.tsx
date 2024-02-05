import fetchMock from 'fetch-mock';

import { useAuthStore } from '@/features/';

import { fetchAPI } from '../fetchApi';

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

  it('adds the BEARER automatically', () => {
    useAuthStore.setState({ token: 'my-token' });

    fetchMock.mock('http://some.api.url/api/v1.0/some/url', 200);

    void fetchAPI('some/url', { body: 'some body' });

    expect(fetchMock.lastOptions()).toEqual({
      body: 'some body',
      headers: {
        Authorization: 'Bearer my-token',
        'Content-Type': 'application/json',
      },
    });
  });

  it('logout if 401 response', async () => {
    useAuthStore.setState({ token: 'my-token' });

    fetchMock.mock('http://some.api.url/api/v1.0/some/url', 401);

    await fetchAPI('some/url');

    expect(useAuthStore.getState().token).toBeNull();
  });
});
