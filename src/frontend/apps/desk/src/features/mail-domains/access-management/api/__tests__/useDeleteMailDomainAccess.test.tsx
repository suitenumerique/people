import { renderHook, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { APIError } from '@/api';
import { AppWrapper } from '@/tests/utils';

import {
  deleteMailDomainAccess,
  useDeleteMailDomainAccess,
} from '../useDeleteMailDomainAccess';

describe('deleteMailDomainAccess', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('deletes the access successfully', async () => {
    fetchMock.deleteOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 204, // No content status
    });

    await deleteMailDomainAccess({
      slug: 'example-slug',
      accessId: '1-1-1-1-1',
    });

    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastUrl()).toContain(
      '/mail-domains/example-slug/accesses/1-1-1-1-1/',
    );
  });

  it('throws an error when the API call fails', async () => {
    fetchMock.deleteOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 500,
      body: { cause: ['Internal server error'] },
    });

    await expect(
      deleteMailDomainAccess({
        slug: 'example-slug',
        accessId: '1-1-1-1-1',
      }),
    ).rejects.toThrow(APIError);
    expect(fetchMock.calls()).toHaveLength(1);
  });
});

describe('useDeleteMailDomainAccess', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('deletes the access and calls onSuccess callback', async () => {
    fetchMock.deleteOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 204, // No content status
    });

    const onSuccess = jest.fn();

    const { result } = renderHook(
      () => useDeleteMailDomainAccess({ onSuccess }),
      {
        wrapper: AppWrapper,
      },
    );

    result.current.mutate({
      slug: 'example-slug',
      accessId: '1-1-1-1-1',
    });

    await waitFor(() => expect(fetchMock.calls()).toHaveLength(1));
    await waitFor(() =>
      expect(onSuccess).toHaveBeenCalledWith(
        undefined,
        { slug: 'example-slug', accessId: '1-1-1-1-1' },
        undefined,
        { client: {}, meta: undefined, mutationKey: undefined },
      ),
    );
    expect(fetchMock.lastUrl()).toContain(
      '/mail-domains/example-slug/accesses/1-1-1-1-1/',
    );
  });

  it('calls onError when the API fails', async () => {
    fetchMock.deleteOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 500,
      body: { cause: ['Internal server error'] },
    });

    const onError = jest.fn();

    const { result } = renderHook(
      () => useDeleteMailDomainAccess({ onError }),
      {
        wrapper: AppWrapper,
      },
    );

    result.current.mutate({
      slug: 'example-slug',
      accessId: '1-1-1-1-1',
    });

    await waitFor(() => expect(fetchMock.calls()).toHaveLength(1));
    await waitFor(() => expect(onError).toHaveBeenCalled());
  });
});
