import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';

import { AppWrapper } from '@/tests/utils';

import { MailDomain, Role } from '../../../domains';
import { Access } from '../../types';
import { AccessesGrid } from '../AccessesGrid';

jest.mock(
  '@/features/mail-domains/access-management/components/AccessAction',
  () => ({
    AccessAction: jest.fn(() => <div>Mock AccessAction</div>),
  }),
);

jest.mock('@/assets/icons/icon-user.svg', () => () => (
  <svg data-testid="icon-user" />
));

const mockMailDomain: MailDomain = {
  id: '1-1-1-1-1',
  name: 'example.com',
  slug: 'example-com',
  status: 'enabled',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  support_email: 'support@example.com',
  abilities: {
    manage_accesses: true,
    get: true,
    patch: true,
    put: true,
    post: true,
    delete: false,
  },
};

const mockAccess: Access = {
  id: '2-1-1-1-1',
  role: Role.ADMIN,
  user: {
    id: '3-1-1-1-1',
    name: 'username1',
    email: 'user1@test.com',
  },
  can_set_role_to: [Role.VIEWER, Role.ADMIN],
};

const mockAccessCreationResponse = {
  count: 2,
  results: [
    mockAccess,
    {
      id: '1-1-1-1-2',
      role: Role.VIEWER,
      user: { id: '22', name: 'username2', email: 'user2@test.com' },
      can_set_role_to: [Role.VIEWER],
    },
  ],
};

describe('AccessesGrid', () => {
  const renderAccessesGrid = (role: Role = Role.ADMIN) =>
    render(<AccessesGrid mailDomain={mockMailDomain} currentRole={role} />, {
      wrapper: AppWrapper,
    });

  afterEach(() => {
    fetchMock.restore();
  });

  it('renders the grid with loading state', async () => {
    fetchMock.getOnce('end:/mail-domains/example-com/accesses/?page=1', {
      status: 200,
      body: mockAccessCreationResponse,
    });

    renderAccessesGrid();

    expect(screen.getByRole('status')).toBeInTheDocument();

    await waitFor(() =>
      expect(screen.queryByRole('status')).not.toBeInTheDocument(),
    );

    expect(screen.getByText('username1')).toBeInTheDocument();
    expect(screen.getByText('username2')).toBeInTheDocument();
  });

  it('renders an error message if the API call fails', async () => {
    fetchMock.getOnce('end:/mail-domains/example-com/accesses/?page=1', {
      status: 500,
      body: { cause: ['Internal server error'] },
    });

    renderAccessesGrid();

    expect(await screen.findByText('Internal server error')).toBeVisible();
  });

  it('applies sorting when a column header is clicked', async () => {
    fetchMock.getOnce('end:/mail-domains/example-com/accesses/?page=1', {
      status: 200,
      body: mockAccessCreationResponse,
    });

    renderAccessesGrid();

    await screen.findByText('username1');

    fetchMock.getOnce(
      'end:/mail-domains/example-com/accesses/?page=1&ordering=user__name',
      {
        status: 200,
        body: mockAccessCreationResponse,
      },
    );

    const nameHeader = screen.getByText('Names');
    await userEvent.click(nameHeader);

    // First load call, then sorting call
    await waitFor(() => expect(fetchMock.calls()).toHaveLength(2));
  });

  it('displays the correct columns and rows in the grid', async () => {
    fetchMock.getOnce('end:/mail-domains/example-com/accesses/?page=1', {
      status: 200,
      body: mockAccessCreationResponse,
    });

    renderAccessesGrid();

    // Waiting for the rows to render
    await screen.findByText('Names');

    expect(screen.getByText('Emails')).toBeInTheDocument();
    expect(screen.getByText('Roles')).toBeInTheDocument();
    expect(screen.getByText('username1')).toBeInTheDocument();
    expect(screen.getByText('user1@test.com')).toBeInTheDocument();
    expect(screen.getByText('Administrator')).toBeInTheDocument();

    expect(screen.getAllByText('Mock AccessAction')).toHaveLength(2);
  });
});
