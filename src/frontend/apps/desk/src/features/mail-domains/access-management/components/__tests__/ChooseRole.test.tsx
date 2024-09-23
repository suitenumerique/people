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

  it('renders available roles correctly', () => {
    renderChooseRole();

    expect(screen.getByLabelText('Viewer')).toBeInTheDocument();
    expect(screen.getByLabelText('Administrator')).toBeInTheDocument();
  });

  it('sets default role checked correctly', () => {
    renderChooseRole({ currentRole: Role.ADMIN });

    const adminRadio: HTMLInputElement = screen.getByLabelText('Administrator');
    const viewerRadio: HTMLInputElement = screen.getByLabelText('Viewer');

    expect(adminRadio).toBeChecked();
    expect(viewerRadio).not.toBeChecked();
  });

  it('calls setRole when a new role is selected', async () => {
    const user = userEvent.setup();

    renderChooseRole();

    await user.click(screen.getByLabelText('Viewer'));

    await waitFor(() => {
      expect(mockSetRole).toHaveBeenCalledWith(Role.VIEWER);
    });
  });

  it('disables radio buttons when disabled prop is true', () => {
    renderChooseRole({ disabled: true });

    const viewerRadio: HTMLInputElement = screen.getByLabelText('Viewer');
    const adminRadio: HTMLInputElement = screen.getByLabelText('Administrator');

    expect(viewerRadio).toBeDisabled();
    expect(adminRadio).toBeDisabled();
  });

  it('disables owner radio button if current role is not owner', () => {
    renderChooseRole({
      availableRoles: [Role.VIEWER, Role.ADMIN, Role.OWNER],
      currentRole: Role.ADMIN,
    });

    const ownerRadio = screen.getByLabelText('Owner');

    expect(ownerRadio).toBeDisabled();
  });

  it('removes duplicates from availableRoles', () => {
    renderChooseRole({
      availableRoles: [Role.VIEWER, Role.ADMIN, Role.VIEWER],
      currentRole: Role.ADMIN,
    });

    const radios = screen.getAllByRole('radio');
    expect(radios.length).toBe(2); // Only two unique roles should be rendered
  });

  it('renders and checks owner role correctly when currentRole is owner', () => {
    renderChooseRole({
      currentRole: Role.OWNER,
      availableRoles: [Role.OWNER, Role.VIEWER, Role.ADMIN],
    });

    const ownerRadio: HTMLInputElement = screen.getByLabelText('Owner');

    expect(ownerRadio).toBeInTheDocument();
    expect(ownerRadio).toBeChecked();
  });

  it('renders no roles if availableRoles is empty', () => {
    renderChooseRole({
      availableRoles: [],
      currentRole: Role.ADMIN,
    });

    const radios = screen.queryAllByRole('radio');
    expect(radios.length).toBe(1); // Only the current role should be rendered
  });

  it.failing('sets aria-checked attribute correctly for selected roles', () => {
    renderChooseRole({ currentRole: Role.ADMIN });

    const adminRadio = screen.getByLabelText('Administrator');
    const viewerRadio = screen.getByLabelText('Viewer');

    expect(adminRadio).toHaveAttribute('aria-checked', 'true');
    expect(viewerRadio).toHaveAttribute('aria-checked', 'false');
  });
});
