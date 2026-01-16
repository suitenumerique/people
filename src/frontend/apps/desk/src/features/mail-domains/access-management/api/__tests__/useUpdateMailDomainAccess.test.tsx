import { renderHook, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { APIError } from '@/api';
import { AppWrapper } from '@/tests/utils';

import { Role } from '../../../domains';
import { Access } from '../../types';
import {
  updateMailDomainAccess,
  useUpdateMailDomainAccess,
} from '../useUpdateMailDomainAccess';

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

describe('updateMailDomainAccess', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('updates the access role successfully', async () => {
    const mockResponse = {
      ...mockAccess,
      role: Role.VIEWER,
    };

    fetchMock.patchOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 200,
      body: mockResponse,
    });

    const result = await updateMailDomainAccess({
      slug: 'example-slug',
      accessId: '1-1-1-1-1',
      role: Role.VIEWER,
    });

    expect(result).toEqual(mockResponse);
    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastUrl()).toContain(
      '/mail-domains/example-slug/accesses/1-1-1-1-1/',
    );
  });

  it('throws an error when the API call fails', async () => {
    fetchMock.patchOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 500,
      body: { cause: ['Internal server error'] },
    });

    await expect(
      updateMailDomainAccess({
        slug: 'example-slug',
        accessId: '1-1-1-1-1',
        role: Role.VIEWER,
      }),
    ).rejects.toThrow(APIError);
    expect(fetchMock.calls()).toHaveLength(1);
  });
});

describe('useUpdateMailDomainAccess', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('updates the role and calls onSuccess callback', async () => {
    const mockResponse = {
      ...mockAccess,
      role: Role.VIEWER,
    };

    fetchMock.patchOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 200,
      body: mockResponse,
    });

    const onSuccess = jest.fn();

    const { result } = renderHook(
      () => useUpdateMailDomainAccess({ onSuccess }),
      {
        wrapper: AppWrapper,
      },
    );

    result.current.mutate({
      slug: 'example-slug',
      accessId: '1-1-1-1-1',
      role: Role.VIEWER,
    });

    await waitFor(() => expect(fetchMock.calls()).toHaveLength(1));
    await waitFor(() =>
      expect(onSuccess).toHaveBeenCalledWith(
        mockResponse, // data
        { slug: 'example-slug', accessId: '1-1-1-1-1', role: Role.VIEWER }, // variables
        undefined, // context
      ),
    );
    expect(fetchMock.lastUrl()).toContain(
      '/mail-domains/example-slug/accesses/1-1-1-1-1/',
    );
  });

  it('calls onError when the API fails', async () => {
    fetchMock.patchOnce('end:/mail-domains/example-slug/accesses/1-1-1-1-1/', {
      status: 500,
      body: { cause: ['Internal server error'] },
    });

    const onError = jest.fn();

    const { result } = renderHook(
      () => useUpdateMailDomainAccess({ onError }),
      {
        wrapper: AppWrapper,
      },
    );

    result.current.mutate({
      slug: 'example-slug',
      accessId: '1-1-1-1-1',
      role: Role.VIEWER,
    });

    await waitFor(() => expect(fetchMock.calls()).toHaveLength(1));
    await waitFor(() => expect(onError).toHaveBeenCalled());
  });
});
