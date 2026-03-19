import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

import { AppWrapper } from '@/tests/utils';

import { Role } from '../../../domains';
import { ChooseRole } from '../ChooseRole';

describe('ChooseRole', () => {
  const mockSetRole = jest.fn();

  const renderChooseRole = (
    props: Partial<React.ComponentProps<typeof ChooseRole>> = {},
  ) => {
    const defaultProps = {
      availableRoles: [Role.VIEWER, Role.ADMIN],
      roleAccess: Role.ADMIN,
      currentRole: Role.ADMIN,
      disabled: false,
      setRole: mockSetRole,
      ...props,
    };

    return render(<ChooseRole {...defaultProps} />, { wrapper: AppWrapper });
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders available roles correctly when we are Administrator', async () => {
    const user = userEvent.setup();
    renderChooseRole();
    expect(
      screen.getByRole('button', { name: 'Administrator' }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Administrator' }));
    expect(
      screen.getByRole('menuitem', { name: 'Viewer' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('menuitem', { name: 'Administrator' }),
    ).toBeInTheDocument();
  });

  it('renders available roles correctly when we are owner', async () => {
    const user = userEvent.setup();
    renderChooseRole({
      currentRole: Role.OWNER,
      roleAccess: Role.OWNER,
    });
    await user.click(screen.getByRole('button', { name: 'Owner' }));
    expect(
      screen.getByRole('menuitem', { name: 'Viewer' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('menuitem', { name: 'Administrator' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: 'Owner' })).toBeInTheDocument();
  });

  it('sets default role checked correctly', () => {
    renderChooseRole({ currentRole: Role.ADMIN });
    const trigger = screen.getByRole('button', { name: 'Administrator' });
    expect(trigger).toBeInTheDocument();
    expect(trigger).toHaveTextContent('Administrator');
  });

  it('calls setRole when a new role is selected', async () => {
    const user = userEvent.setup();
    renderChooseRole();
    await user.click(screen.getByRole('button', { name: 'Administrator' }));
    await user.click(screen.getByRole('menuitem', { name: 'Viewer' }));

    await waitFor(() => {
      expect(mockSetRole).toHaveBeenCalledWith(Role.VIEWER);
    });
  });

  it('disables trigger button when disabled prop is true', () => {
    renderChooseRole({ disabled: true });
    const trigger = screen.getByRole('button', { name: 'Administrator' });
    expect(trigger).toBeDisabled();
  });

  it('disables owner menu option when current role is not owner', async () => {
    const user = userEvent.setup();
    renderChooseRole({
      availableRoles: [Role.VIEWER, Role.ADMIN, Role.OWNER],
      currentRole: Role.ADMIN,
    });
    await user.click(screen.getByRole('button', { name: 'Administrator' }));
    const ownerOption = screen.getByRole('menuitem', { name: 'Owner' });
    expect(ownerOption).toHaveAttribute('aria-disabled', 'true');
  });

  it('removes duplicates from availableRoles', async () => {
    const user = userEvent.setup();
    renderChooseRole({
      availableRoles: [Role.VIEWER, Role.ADMIN, Role.VIEWER],
      currentRole: Role.ADMIN,
    });
    await user.click(screen.getByRole('button', { name: 'Administrator' }));
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems).toHaveLength(2);
  });

  it('renders and checks owner role correctly when currentRole is owner', () => {
    renderChooseRole({
      currentRole: Role.OWNER,
      roleAccess: Role.OWNER,
      availableRoles: [Role.OWNER, Role.VIEWER, Role.ADMIN],
    });
    const trigger = screen.getByRole('button', { name: 'Owner' });
    expect(trigger).toBeInTheDocument();
    expect(trigger).toHaveTextContent('Owner');
  });

  it('renders only current role when availableRoles is empty', async () => {
    const user = userEvent.setup();
    renderChooseRole({
      availableRoles: [],
      currentRole: Role.ADMIN,
    });
    await user.click(screen.getByRole('button', { name: 'Administrator' }));
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems).toHaveLength(1);
  });
});
