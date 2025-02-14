import { useToastProvider } from '@openfun/cunningham-react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';
import React from 'react';

import { AppWrapper } from '@/tests/utils';

import { MailDomain, Role } from '../../../domains';
import { ModalNewAccess } from '../ModalNewAccess';

const domain: MailDomain = {
  id: '897-9879-986789-89798-897',
  name: 'Domain test',
  created_at: '121212',
  updated_at: '121212',
  slug: 'test-domain',
  status: 'pending',
  support_email: 'sfs@test-domain.fr',
  abilities: {
    get: true,
    patch: true,
    put: true,
    post: true,
    delete: true,
    manage_accesses: true,
  },
};

jest.mock('@openfun/cunningham-react', () => ({
  ...jest.requireActual('@openfun/cunningham-react'),
  useToastProvider: jest.fn(),
}));

jest.mock('../../api', () => ({
  useCreateInvitation: jest.fn(() => ({ mutateAsync: jest.fn() })),
}));

jest.mock('@/features/mail-domains/access-management', () => ({
  usePostMailDomainAccess: jest.fn(() => ({ mutateAsync: jest.fn() })),
}));

describe('ModalNewAccess', () => {
  const mockOnClose = jest.fn();
  const mockToast = jest.fn();
  const mockPostMailDomainAccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    fetchMock.restore();
    (useToastProvider as jest.Mock).mockReturnValue({ toast: mockToast });
  });

  const renderModalNewAccess = () => {
    return render(
      <ModalNewAccess
        mailDomain={domain}
        currentRole={Role.ADMIN}
        onClose={mockOnClose}
      />,
      { wrapper: AppWrapper },
    );
  };

  it('renders the modal with all elements', () => {
    renderModalNewAccess();
    expect(screen.getByText('Add a new access')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Add to domain/i }),
    ).toBeInTheDocument();
  });

  it('calls onClose when Cancel is clicked', async () => {
    renderModalNewAccess();
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    await userEvent.click(cancelButton);
    await waitFor(() => expect(mockOnClose).toHaveBeenCalledTimes(1), {
      timeout: 3000,
    });
  });

  it('displays a success toast when access is successfully added', async () => {
    mockPostMailDomainAccess.mockResolvedValueOnce({ success: true });
    renderModalNewAccess();
    const addButton = screen.getByRole('button', { name: /Add to domain/i });
    await userEvent.click(addButton);
    await waitFor(() => expect(mockToast).toHaveBeenCalled());
  });

  it('displays an error toast when adding access fails', async () => {
    mockPostMailDomainAccess.mockRejectedValueOnce(
      new Error('Failed to add access'),
    );
    renderModalNewAccess();
    const addButton = screen.getByRole('button', { name: /Add to domain/i });
    await userEvent.click(addButton);
    await waitFor(() => expect(mockToast).toHaveBeenCalled());
  });
});
