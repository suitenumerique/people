import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AppWrapper } from '@/tests/utils';

import { MailDomain, Role } from '../../../domains';
import { Access } from '../../types';
import { AccessAction } from '../AccessAction';
import { ModalDelete } from '../ModalDelete';
import { ModalRole } from '../ModalRole';

jest.mock('../ModalRole', () => ({
  ModalRole: jest.fn(() => <div>Mock ModalRole</div>),
}));

jest.mock('../ModalDelete', () => ({
  ModalDelete: jest.fn(() => <div>Mock ModalDelete</div>),
}));

describe('AccessAction', () => {
  const mockMailDomain: MailDomain = {
    id: '1-1-1-1-1',
    name: 'example.com',
    slug: 'example-com',
    status: 'enabled',
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
    role: Role.ADMIN,
    user: {
      id: '11',
      name: 'username1',
      email: 'user1@test.com',
    },
    can_set_role_to: [Role.VIEWER, Role.ADMIN],
  };

  const renderAccessAction = (
    currentRole: Role = Role.ADMIN,
    access: Access = mockAccess,
    mailDomain = mockMailDomain,
  ) =>
    render(
      <AccessAction
        access={access}
        currentRole={currentRole}
        mailDomain={mailDomain}
      />,
      { wrapper: AppWrapper },
    );

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders nothing for unauthorized roles', () => {
    renderAccessAction(Role.VIEWER);

    expect(
      screen.queryByLabelText('Open the access options modal'),
    ).not.toBeInTheDocument();

    renderAccessAction(Role.ADMIN, { ...mockAccess, role: Role.OWNER });

    expect(
      screen.queryByLabelText('Open the access options modal'),
    ).not.toBeInTheDocument();
  });

  it('does not render "Update role" button when mailDomain lacks "put" and "patch" abilities', async () => {
    const mailDomainWithoutUpdate = {
      ...mockMailDomain,
      abilities: {
        ...mockMailDomain.abilities,
        put: false,
        patch: false,
      },
    };

    renderAccessAction(Role.ADMIN, mockAccess, mailDomainWithoutUpdate);

    const openButton = screen.getByLabelText('Open the access options modal');
    await userEvent.click(openButton);

    expect(
      screen.queryByLabelText(
        'Open the modal to update the role of this access',
      ),
    ).not.toBeInTheDocument();
  });

  it('opens the role update modal with correct props when "Update role" is clicked', async () => {
    renderAccessAction();

    const openButton = screen.getByLabelText('Open the access options modal');
    await userEvent.click(openButton);

    const updateRoleButton = screen.getByLabelText(
      'Open the modal to update the role of this access',
    );
    await userEvent.click(updateRoleButton);

    expect(screen.getByText('Mock ModalRole')).toBeInTheDocument();
    expect(ModalRole).toHaveBeenCalledWith(
      expect.objectContaining({
        access: mockAccess,
        currentRole: Role.ADMIN,
        slug: mockMailDomain.slug,
        onClose: expect.any(Function),
      }),
      undefined,
    );
  });

  it('does not render "Remove from domain" button when mailDomain lacks "delete" ability', async () => {
    const mailDomainWithoutDelete = {
      ...mockMailDomain,
      abilities: {
        ...mockMailDomain.abilities,
        delete: false,
      },
    };

    renderAccessAction(Role.ADMIN, mockAccess, mailDomainWithoutDelete);

    const openButton = screen.getByLabelText('Open the access options modal');
    await userEvent.click(openButton);

    expect(
      screen.queryByLabelText('Open the modal to delete this access'),
    ).not.toBeInTheDocument();
  });

  it('opens the delete modal with correct props when "Remove from domain" is clicked', async () => {
    renderAccessAction();

    const openButton = screen.getByLabelText('Open the access options modal');
    await userEvent.click(openButton);

    const removeButton = screen.getByLabelText(
      'Open the modal to delete this access',
    );
    await userEvent.click(removeButton);

    expect(screen.getByText('Mock ModalDelete')).toBeInTheDocument();
    expect(ModalDelete).toHaveBeenCalledWith(
      expect.objectContaining({
        access: mockAccess,
        currentRole: Role.ADMIN,
        mailDomain: mockMailDomain,
        onClose: expect.any(Function),
      }),
      undefined,
    );
  });

  it('toggles the DropButton', async () => {
    renderAccessAction();

    const openButton = screen.getByLabelText('Open the access options modal');
    expect(screen.queryByText('Update role')).toBeNull();

    await userEvent.click(openButton);
    expect(screen.getByText('Update role')).toBeInTheDocument();

    // Close the dropdown
    await userEvent.click(openButton);
    expect(screen.queryByText('Update role')).toBeNull();
  });
});
