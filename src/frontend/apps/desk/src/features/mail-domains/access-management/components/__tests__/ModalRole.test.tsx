import { VariantType, useToastProvider } from '@gouvfr-lasuite/cunningham-react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';
import React from 'react';

import { AppWrapper } from '@/tests/utils';

import { Role } from '../../../domains';
import { useWhoAmI } from '../../hooks/useWhoAmI';
import { Access } from '../../types';
import { ModalRole } from '../ModalRole';

jest.mock('@gouvfr-lasuite/cunningham-react', () => ({
  ...jest.requireActual('@gouvfr-lasuite/cunningham-react'),
  useToastProvider: jest.fn(),
}));
jest.mock('../../hooks/useWhoAmI');

describe('ModalRole', () => {
  const access: Access = {
    id: '1-1-1-1-1-1',
    role: Role.ADMIN,
    user: {
      id: '2-1-1-1-1-1',
      name: 'username1',
      email: 'user1@test.com',
    },
    can_set_role_to: [Role.VIEWER, Role.ADMIN],
  };

  const mockOnClose = jest.fn();
  const mockToast = jest.fn();

  const renderModalRole = (
    isLastOwner = false,
    isOtherOwner = false,
    props?: Partial<React.ComponentProps<typeof ModalRole>>,
  ) => {
    (useToastProvider as jest.Mock).mockReturnValue({ toast: mockToast });
    (useWhoAmI as jest.Mock).mockReturnValue({
      isLastOwner,
      isOtherOwner,
    });

    return render(
      <ModalRole
        access={access}
        currentRole={props?.currentRole ?? Role.ADMIN}
        onClose={mockOnClose}
        slug="domain-slug"
      />,
      { wrapper: AppWrapper },
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    fetchMock.restore();
  });

  it('renders the modal with all elements', () => {
    renderModalRole();

    expect(screen.getByText('Update the role')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Validate/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText('Radio buttons to update the roles'),
    ).toBeInTheDocument();
  });

  it('calls the close function when Cancel is clicked', async () => {
    renderModalRole();

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    await userEvent.click(cancelButton);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  it('updates the role and closes the modal when Validate is clicked', async () => {
    fetchMock.patch(`end:mail-domains/domain-slug/accesses/1-1-1-1-1-1/`, {
      status: 200,
      body: {
        id: '1-1-1-1-1-1',
        role: Role.VIEWER,
      },
    });

    renderModalRole();

    const validateButton = screen.getByRole('button', { name: /Validate/i });
    await userEvent.click(validateButton);

    await waitFor(() => {
      expect(fetchMock.calls().length).toBe(1);
    });
    expect(fetchMock.lastCall()?.[0]).toContain(
      '/mail-domains/domain-slug/accesses/1-1-1-1-1-1/',
    );

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    expect(mockToast).toHaveBeenCalledWith(
      'The role has been updated',
      VariantType.SUCCESS,
      { duration: 4000 },
    );
  });

  it('shows error message when update fails', async () => {
    fetchMock.patch(`end:mail-domains/domain-slug/accesses/1-1-1-1-1-1/`, {
      status: 400,
      body: {
        cause: ['Error updating role'],
      },
    });

    renderModalRole();

    const validateButton = screen.getByRole('button', { name: /Validate/i });
    await userEvent.click(validateButton);

    await waitFor(() => {
      expect(fetchMock.calls().length).toBe(1);
    });

    expect(screen.getByText('Error updating role')).toBeInTheDocument();
  });

  it('displays the available roles and ensures no duplicates', () => {
    renderModalRole();

    const radioButtons = screen.getAllByRole('radio');
    expect(radioButtons.length).toBe(2); // Only two roles: Viewer and Admin
    expect(screen.getByLabelText('Administrator')).toBeInTheDocument();
    expect(screen.getByLabelText('Viewer')).toBeInTheDocument();
  });
});
