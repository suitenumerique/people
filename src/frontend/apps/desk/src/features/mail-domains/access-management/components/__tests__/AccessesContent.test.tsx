import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter } from 'next/navigation';

import { AccessesGrid } from '@/features/mail-domains/access-management';
import { AppWrapper } from '@/tests/utils';

import { MailDomain, Role } from '../../../domains';
import { AccessesContent } from '../AccessesContent';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock(
  '@/features/mail-domains/access-management/components/AccessesGrid',
  () => ({
    AccessesGrid: jest.fn(() => <div>Mock AccessesGrid</div>),
  }),
);

jest.mock('@/features/mail-domains/assets/mail-domains-logo.svg', () => () => (
  <svg data-testid="mail-domains-logo" />
));

describe('AccessesContent', () => {
  const mockRouterPush = jest.fn();

  const mockMailDomain: MailDomain = {
    id: '1-1-1-1-1',
    name: 'example.com',
    slug: 'example-com',
    status: 'enabled',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    abilities: {
      get: true,
      patch: true,
      put: true,
      post: true,
      delete: true,
      manage_accesses: true,
    },
  };

  const renderAccessesContent = (
    currentRole: Role = Role.ADMIN,
    mailDomain: MailDomain = mockMailDomain,
  ) =>
    render(
      <AccessesContent currentRole={currentRole} mailDomain={mailDomain} />,
      {
        wrapper: AppWrapper,
      },
    );

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockRouterPush,
    });
  });

  it('renders the top banner and accesses grid correctly', () => {
    renderAccessesContent();

    expect(screen.getByText(mockMailDomain.name)).toBeInTheDocument();
    expect(screen.getByTestId('mail-domains-logo')).toBeInTheDocument();
    expect(screen.getByText('Mock AccessesGrid')).toBeInTheDocument();
  });

  it('renders the "Manage mailboxes" button when the user has access', () => {
    renderAccessesContent();

    const manageMailboxesButton = screen.getByRole('button', {
      name: /Manage example.com domain mailboxes/,
    });

    expect(manageMailboxesButton).toBeInTheDocument();

    expect(AccessesGrid).toHaveBeenCalledWith(
      { currentRole: Role.ADMIN, mailDomain: mockMailDomain },
      {}, // adding this empty object is necessary to load jest context and that AccessesGrid is a mock
    );
  });

  it('does not render the "Manage mailboxes" button if the user lacks manage_accesses ability', () => {
    const mailDomainWithoutAccess = {
      ...mockMailDomain,
      abilities: {
        ...mockMailDomain.abilities,
        manage_accesses: false,
      },
    };

    renderAccessesContent(Role.ADMIN, mailDomainWithoutAccess);

    expect(
      screen.queryByRole('button', {
        name: /Manage mailboxes/i,
      }),
    ).not.toBeInTheDocument();
  });

  it('navigates to the mailboxes management page when "Manage mailboxes" is clicked', async () => {
    renderAccessesContent();

    const manageMailboxesButton = screen.getByRole('button', {
      name: /Manage example.com domain mailboxes/,
    });

    await userEvent.click(manageMailboxesButton);

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith(`/mail-domains/example-com/`);
    });
  });
});
