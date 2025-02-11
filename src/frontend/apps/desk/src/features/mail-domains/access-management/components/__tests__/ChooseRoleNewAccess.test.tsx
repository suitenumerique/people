import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { AppWrapper } from '@/tests/utils';
import { Role } from '../../domains';
import { ChooseRoleNewAccess } from '../ChooseRoleNewAccess';

describe('ChooseRoleNewAccess', () => {
  const mockSetRole = jest.fn();

  const renderChooseRoleNewAccess = (
    props: Partial<React.ComponentProps<typeof ChooseRoleNewAccess>> = {},
  ) => {
    const defaultProps = {
      defaultRole: Role.ADMIN,
      currentRole: Role.ADMIN,
      disabled: false,
      setRole: mockSetRole,
      ...props,
    };

    return render(<ChooseRoleNewAccess {...defaultProps} />, { wrapper: AppWrapper });
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders available roles correctly', () => {
    renderChooseRoleNewAccess();
    expect(screen.getByLabelText('Viewer')).toBeInTheDocument();
    expect(screen.getByLabelText('Administrator')).toBeInTheDocument();
  });

  it('renders Owner role only if current role is Owner', () => {
    renderChooseRoleNewAccess({ currentRole: Role.OWNER });
    expect(screen.getByLabelText('Owner')).toBeInTheDocument();
  });

  it('sets default role checked correctly', () => {
    renderChooseRoleNewAccess({ defaultRole: Role.ADMIN });
    const adminRadio = screen.getByLabelText('Administrator');
    expect(adminRadio).toBeChecked();
  });

  it('calls setRole when a new role is selected', async () => {
    const user = userEvent.setup();
    renderChooseRoleNewAccess();
    await user.click(screen.getByLabelText('Viewer'));
    await waitFor(() => {
      expect(mockSetRole).toHaveBeenCalledWith(Role.VIEWER);
    });
  });

  it('disables radio buttons when disabled prop is true', () => {
    renderChooseRoleNewAccess({ disabled: true });
    expect(screen.getByLabelText('Viewer')).toBeDisabled();
    expect(screen.getByLabelText('Administrator')).toBeDisabled();
  });

  it('disables Owner radio button if current role is not Owner', () => {
    renderChooseRoleNewAccess({ currentRole: Role.ADMIN });
    expect(screen.getByLabelText('Owner')).toBeDisabled();
  });
});
