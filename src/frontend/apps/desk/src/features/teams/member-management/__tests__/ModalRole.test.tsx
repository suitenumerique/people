import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';

import { useAuthStore } from '@/core/auth';
import { Role } from '@/features/teams/team-management';
import { AppWrapper } from '@/tests/utils';

import { ModalRole } from '../components/ModalRole';
import { Access } from '../types';

const toast = jest.fn();
jest.mock('@openfun/cunningham-react', () => ({
  ...jest.requireActual('@openfun/cunningham-react'),
  useToastProvider: () => ({
    toast,
  }),
}));

HTMLDialogElement.prototype.showModal = jest.fn(function mock(
  this: HTMLDialogElement,
) {
  this.open = true;
});

const access: Access = {
  id: '789',
  role: Role.ADMIN,
  user: {
    id: '11',
    name: 'username1',
    email: 'user1@test.com',
  },
  abilities: {
    set_role_to: [Role.MEMBER, Role.ADMIN],
  } as any,
};

describe('ModalRole', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('checks the cancel button', async () => {
    const onClose = jest.fn();
    render(
      <ModalRole
        access={access}
        currentRole={Role.ADMIN}
        onClose={onClose}
        teamId="123"
      />,
      {
        wrapper: AppWrapper,
      },
    );

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Cancel',
      }),
    );

    expect(onClose).toHaveBeenCalled();
  });

  it('updates the role successfully', async () => {
    fetchMock.mock(`end:/teams/123/accesses/789/`, {
      status: 200,
      ok: true,
    });

    const onClose = jest.fn();
    render(
      <ModalRole
        access={access}
        currentRole={Role.OWNER}
        onClose={onClose}
        teamId="123"
      />,
      { wrapper: AppWrapper },
    );

    const select = screen.getByRole('combobox', { name: /role/i });
    expect(select).toBeInTheDocument();
    expect(screen.getByText('Administrator')).toBeInTheDocument();

    await userEvent.click(select);
    const memberOption = await screen.findByRole('option', { name: 'Member' });
    await userEvent.click(memberOption);

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Validate',
      }),
    );

    await waitFor(() => {
      expect(toast).toHaveBeenCalledWith(
        'The role has been updated',
        'success',
        {
          duration: 4000,
        },
      );
    });

    expect(fetchMock.lastUrl()).toContain(`/teams/123/accesses/789/`);
    expect(onClose).toHaveBeenCalled();
  });

  it('fails to update the role', async () => {
    fetchMock.patchOnce(`end:/teams/123/accesses/789/`, {
      status: 500,
      body: {
        detail: 'The server is totally broken',
      },
    });

    render(
      <ModalRole
        access={access}
        currentRole={Role.OWNER}
        onClose={jest.fn()}
        teamId="123"
      />,
      { wrapper: AppWrapper },
    );

    const select = screen.getByRole('combobox', { name: /role/i });
    await userEvent.click(select);
    const memberOption = await screen.findByRole('option', { name: 'Member' });
    await userEvent.click(memberOption);

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Validate',
      }),
    );

    expect(
      await screen.findByText('The server is totally broken'),
    ).toBeInTheDocument();
  });

  it('checks the render when last owner', () => {
    useAuthStore.setState({
      userData: access.user,
    });

    const access2: Access = {
      ...access,
      role: Role.OWNER,
      abilities: {
        set_role_to: [],
      } as any,
    };

    render(
      <ModalRole
        access={access2}
        currentRole={Role.OWNER}
        onClose={jest.fn()}
        teamId="123"
      />,
      { wrapper: AppWrapper },
    );

    expect(
      screen.getByText(
        'You are the sole owner of this group. Make another member the group owner, before you can change your own role.',
      ),
    ).toBeInTheDocument();

    const select = screen.getByRole('combobox', { name: /role/i });
    expect(select).toHaveAttribute('disabled');
    expect(
      screen.getByRole('button', {
        name: 'Validate',
      }),
    ).toBeDisabled();
  });

  it('checks the render when it is another owner', () => {
    useAuthStore.setState({
      userData: {
        id: '12',
        name: 'username2',
        email: 'username2@test.com',
      },
    });

    const access2: Access = {
      ...access,
      role: Role.OWNER,
    };

    render(
      <ModalRole
        access={access2}
        currentRole={Role.OWNER}
        onClose={jest.fn()}
        teamId="123"
      />,
      { wrapper: AppWrapper },
    );

    expect(
      screen.getByText('You cannot update the role of other owner.'),
    ).toBeInTheDocument();

    const select = screen.getByRole('combobox', { name: /role/i });
    expect(select).toHaveAttribute('disabled');

    expect(
      screen.getByRole('button', {
        name: 'Validate',
      }),
    ).toBeDisabled();
  });

  it('checks the render when current user is admin', async () => {
    render(
      <ModalRole
        access={access}
        currentRole={Role.ADMIN}
        onClose={jest.fn()}
        teamId="123"
      />,
      { wrapper: AppWrapper },
    );

    const select = screen.getByRole('combobox', { name: /role/i });
    expect(select).toBeEnabled();
    await userEvent.click(select);

    const adminOption = screen.getByRole('option', { name: 'Administrator' });
    expect(adminOption).toBeEnabled();
  });
});
