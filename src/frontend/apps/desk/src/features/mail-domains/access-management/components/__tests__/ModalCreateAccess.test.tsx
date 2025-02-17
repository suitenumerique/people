import { useToastProvider } from '@openfun/cunningham-react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';
import React from 'react';

import { useCreateMailDomainAccess } from '@/features/mail-domains/access-management';
import { AppWrapper } from '@/tests/utils';

import { MailDomain, Role } from '../../../domains';
import { ModalCreateAccess } from '../ModalCreateAccess';

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
  useCreateMailDomainAccess: jest.fn(),
}));

describe('ModalCreateAccess', () => {
  const mockOnClose = jest.fn();
  const mockToast = jest.fn();
  const mockCreateMailDomainAccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    fetchMock.restore();
    (useToastProvider as jest.Mock).mockReturnValue({ toast: mockToast });

    (useCreateMailDomainAccess as jest.Mock).mockReturnValue({
      mutateAsync: mockCreateMailDomainAccess,
    });
  });

  const renderModalCreateAccess = () => {
    return render(
      <ModalCreateAccess
        mailDomain={domain}
        currentRole={Role.ADMIN}
        onClose={mockOnClose}
      />,
      { wrapper: AppWrapper },
    );
  };

  it('renders the modal with all elements', () => {
    renderModalCreateAccess();
    expect(screen.getByText('Add a new access')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Add to domain/i }),
    ).toBeInTheDocument();
  });

  it('calls onClose when Cancel is clicked', async () => {
    renderModalCreateAccess();
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    await userEvent.click(cancelButton);
    await waitFor(() => expect(mockOnClose).toHaveBeenCalledTimes(1), {
      timeout: 3000,
    });
  });
});
