import { renderHook, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { APIError } from '@/api';
import { AppWrapper } from '@/tests/utils';

import { Role } from '../../../domains';
import { Access } from '../../types';
import {
  getMailDomainAccesses,
  useMailDomainAccesses,
} from '../useMailDomainAccesses';

const mockAccess: Access = {
  id: '1-1-1-1-1',
  role: Role.ADMIN,
  user: {
    id: '2-1-1-1-1',
    name: 'username1',
    email: 'user1@test.com',
  },
  can_set_role_to: [Role.VIEWER, Role.ADMIN],
};

describe('getMailDomainAccesses', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('fetches the list of accesses successfully', async () => {
    const mockResponse = {
      count: 2,
      results: [
        mockAccess,
        {
          id: '2',
          role: Role.VIEWER,
          user: {
            id: '12',
            name: 'username2',
            email: 'user2@test.com',
          },
          can_set_role_to: [Role.VIEWER],
        },
      ],
    };

    fetchMock.getOnce('end:/mail-domains/example-slug/accesses/?page=1', {
      status: 200,
      body: mockResponse,
    });

    const result = await getMailDomainAccesses({
      page: 1,
      slug: 'example-slug',
    });

    expect(result).toEqual(mockResponse);
    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastUrl()).toContain(
      '/mail-domains/example-slug/accesses/?page=1',
    );
  });

  it('throws an error when the API call fails', async () => {
    fetchMock.getOnce('end:/mail-domains/example-slug/accesses/?page=1', {
      status: 500,
      body: { cause: ['Internal server error'] },
    });

    await expect(
      getMailDomainAccesses({ page: 1, slug: 'example-slug' }),
    ).rejects.toThrow(APIError);
    expect(fetchMock.calls()).toHaveLength(1);
  });
});

describe('useMailDomainAccesses', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('fetches and returns the accesses data using the hook', async () => {
    const mockResponse = {
      count: 2,
      results: [
        mockAccess,
        {
          id: '2',
          role: Role.VIEWER,
          user: { id: '12', name: 'username2', email: 'user2@test.com' },
          can_set_role_to: [Role.VIEWER],
        },
      ],
    };

    fetchMock.getOnce('end:/mail-domains/example-slug/accesses/?page=1', {
      status: 200,
      body: mockResponse,
    });

    const { result } = renderHook(
      () => useMailDomainAccesses({ page: 1, slug: 'example-slug' }),
      {
        wrapper: AppWrapper,
      },
    );

    await waitFor(() => result.current.isSuccess);

    await waitFor(() => expect(result.current.data).toEqual(mockResponse));
    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastUrl()).toContain(
      '/mail-domains/example-slug/accesses/?page=1',
    );
  });

  it('handles an API error properly with the hook', async () => {
    fetchMock.getOnce('end:/mail-domains/example-slug/accesses/?page=1', {
      status: 500,
      body: { cause: ['Internal server error'] },
    });

    const { result } = renderHook(
      () => useMailDomainAccesses({ page: 1, slug: 'example-slug' }),
      {
        wrapper: AppWrapper,
      },
    );

    await waitFor(() => result.current.isError);

    await waitFor(() => expect(result.current.error).toBeInstanceOf(APIError));
    expect(result.current.error?.message).toBe('Failed to get the accesses');
    expect(fetchMock.calls()).toHaveLength(1);
  });
});
