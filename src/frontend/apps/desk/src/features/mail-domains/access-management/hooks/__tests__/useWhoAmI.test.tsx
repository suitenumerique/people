import { renderHook } from '@testing-library/react';

import { useAuthStore } from '@/core/auth/useAuthStore';

import { Role } from '../../../domains';
import { useWhoAmI } from '../../hooks/useWhoAmI';
import { Access } from '../../types';

jest.mock('@/core/auth/useAuthStore');

const mockAccess: Access = {
  id: '1-1-1-1-1',
  user: {
    id: '2-1-1-1-1',
    name: 'User One',
    email: 'user1@example.com',
  },
  role: Role.ADMIN,
  can_set_role_to: [Role.VIEWER, Role.ADMIN],
};

describe('useWhoAmI', () => {
  beforeEach(() => {
    (useAuthStore as unknown as jest.Mock).mockReturnValue({
      authenticated: true,
      userData: {
        id: '2-1-1-1-1',
        name: 'Current User',
        email: 'currentuser@example.com',
      },
    });
  });

  const renderUseWhoAmI = (access: Access) =>
    renderHook(() => useWhoAmI(access));

  it('identifies if the current user is themselves', () => {
    const { result } = renderUseWhoAmI(mockAccess);
    expect(result.current.isMyself).toBeTruthy();
  });

  it('identifies if the current user is not themselves', () => {
    const { result } = renderUseWhoAmI({
      ...mockAccess,
      user: { ...mockAccess.user, id: '2-1-1-1-2' },
    });
    expect(result.current.isMyself).toBeFalsy();
  });

  it('identifies if the current user is the last owner', () => {
    const accessAsLastOwner = {
      ...mockAccess,
      role: Role.OWNER,
      can_set_role_to: [],
    };
    const { result } = renderUseWhoAmI(accessAsLastOwner);
    expect(result.current.isLastOwner).toBeTruthy();
  });

  it('identifies if the current user is not the last owner', () => {
    const accessAsNonOwner = { ...mockAccess, role: Role.ADMIN };
    const { result } = renderUseWhoAmI(accessAsNonOwner);
    expect(result.current.isLastOwner).toBeFalsy();
  });

  it('identifies if the current user is another owner', () => {
    const accessOfOtherOwner = {
      ...mockAccess,
      role: Role.OWNER,
      user: { ...mockAccess.user, id: '2-1-1-1-2' },
    };

    const { result } = renderUseWhoAmI(accessOfOtherOwner);
    expect(result.current.isOtherOwner).toBeTruthy();
  });

  it('identifies if the current user is not another owner', () => {
    const nonOwnerAccess = {
      ...mockAccess,
      role: Role.ADMIN,
      user: { ...mockAccess.user, id: '2-1-1-1-2' },
    };
    const { result } = renderUseWhoAmI(nonOwnerAccess);
    expect(result.current.isOtherOwner).toBeFalsy();
  });
});
