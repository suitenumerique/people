import { VariantType, useToastProvider } from '@openfun/cunningham-react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';
import { useRouter } from 'next/navigation';

import { Access } from '@/features/mail-domains/access-management';
import { AppWrapper } from '@/tests/utils';

import { MailDomain, Role } from '../../../domains';
import { useWhoAmI } from '../../hooks/useWhoAmI';
import { ModalDelete, ModalDeleteProps } from '../ModalDelete';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@openfun/cunningham-react', () => ({
  ...jest.requireActual('@openfun/cunningham-react'),
  useToastProvider: jest.fn(),
}));

jest.mock('../../hooks/useWhoAmI', () => ({
  useWhoAmI: jest.fn(),
}));

describe('ModalDelete', () => {
  const mockRouterPush = jest.fn();
  const mockClose = jest.fn();
  const mockToast = jest.fn();

  const mockMailDomain: MailDomain = {
    id: '1-1-1-1-1',
    name: 'example.com',
    slug: 'example-com',
    status: 'enabled',
    count_mailboxes: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    support_email: 'support@example.com',
    abilities: {
      get: true,
      patch: true,
      put: true,
      post: true,
      delete: true,
      manage_accesses: true,
    },
  };

  const mockAccess: Access = {
    id: '2-1-1-1-1',
    user: { id: '3-1-1-1-1', name: 'username1', email: 'user1@test.com' },
    role: Role.ADMIN,
    can_set_role_to: [Role.ADMIN, Role.VIEWER],
  };

  const renderModalDelete = (props: Partial<ModalDeleteProps> = {}) =>
    render(
      <ModalDelete
        access={mockAccess}
        currentRole={Role.ADMIN}
        onClose={mockClose}
        mailDomain={mockMailDomain}
        {...props}
      />,
      {
        wrapper: AppWrapper,
      },
    );

  beforeEach(() => {
    jest.clearAllMocks();
    fetchMock.restore();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockRouterPush,
    });
    (useToastProvider as jest.Mock).mockReturnValue({ toast: mockToast });
    (useWhoAmI as jest.Mock).mockReturnValue({
      isMyself: false,
      isLastOwner: false,
      isOtherOwner: false,
    });
  });

  it('renders the modal with the correct content', () => {
    renderModalDelete();

    expect(
      screen.getByText('Remove this access from the domain'),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'Are you sure you want to remove this access from the example.com domain?',
      ),
    ).toBeInTheDocument();
    expect(screen.getByText('username1')).toBeInTheDocument();
  });

  it('calls onClose when Cancel is clicked', async () => {
    renderModalDelete();

    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    await userEvent.click(cancelButton);

    expect(mockClose).toHaveBeenCalledTimes(1);
  });

  it('sends a delete request when "Remove from the domain" is clicked', async () => {
    fetchMock.deleteOnce('end:/mail-domains/example-com/accesses/2-1-1-1-1/', {
      status: 204,
    });

    renderModalDelete();

    const removeButton = screen.getByRole('button', {
      name: 'Remove from the domain',
    });
    await userEvent.click(removeButton);

    await waitFor(() => {
      expect(fetchMock.calls().length).toBe(1);
    });
    expect(fetchMock.lastUrl()).toContain(
      '/mail-domains/example-com/accesses/2-1-1-1-1/',
    );
  });

  it('displays error message when API call fails', async () => {
    fetchMock.deleteOnce('end:/mail-domains/example-com/accesses/2-1-1-1-1/', {
      status: 500,
      body: { cause: ['Failed to delete access'] },
    });

    renderModalDelete();

    const removeButton = screen.getByRole('button', {
      name: 'Remove from the domain',
    });
    await userEvent.click(removeButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to delete access')).toBeInTheDocument();
    });
  });

  it('disables the remove button if the user is the last owner', () => {
    (useWhoAmI as jest.Mock).mockReturnValue({
      isMyself: false,
      isLastOwner: true,
      isOtherOwner: false,
    });

    renderModalDelete();

    const removeButton = screen.getByRole('button', {
      name: 'Remove from the domain',
    });
    expect(removeButton).toBeDisabled();
    expect(
      screen.getByText(
        'You are the last owner, you cannot be removed from your domain.',
      ),
    ).toBeInTheDocument();
  });

  it('disables the remove button if the user is not allowed to remove another owner', () => {
    (useWhoAmI as jest.Mock).mockReturnValue({
      isMyself: false,
      isLastOwner: false,
      isOtherOwner: true,
    });

    renderModalDelete();

    const removeButton = screen.getByRole('button', {
      name: 'Remove from the domain',
    });
    expect(removeButton).toBeDisabled();
    expect(
      screen.getByText('You cannot remove other owner.'),
    ).toBeInTheDocument();
  });

  it('redirects to home page if user removes themselves', async () => {
    (useWhoAmI as jest.Mock).mockReturnValue({
      isMyself: true,
      isLastOwner: false,
      isOtherOwner: false,
    });

    fetchMock.deleteOnce('end:/mail-domains/example-com/accesses/2-1-1-1-1/', {
      status: 204,
    });

    renderModalDelete();

    const removeButton = screen.getByRole('button', {
      name: 'Remove from the domain',
    });
    await userEvent.click(removeButton);

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/');
    });
  });

  it('shows success toast and calls onClose after successful deletion', async () => {
    fetchMock.deleteOnce('end:/mail-domains/example-com/accesses/2-1-1-1-1/', {
      status: 204,
    });

    renderModalDelete();

    const removeButton = screen.getByRole('button', {
      name: 'Remove from the domain',
    });
    await userEvent.click(removeButton);

    await waitFor(() => {
      expect(fetchMock.calls().length).toBe(1);
    });
    expect(mockToast).toHaveBeenCalledWith(
      'The access has been removed from the domain',
      VariantType.SUCCESS,
      { duration: 4000 },
    );
    expect(mockClose).toHaveBeenCalled();
  });
});
