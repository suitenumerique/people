import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/navigation';

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

  it('renders the accesses grid correctly', () => {
    renderAccessesContent();

    expect(screen.getByText('Mock AccessesGrid')).toBeInTheDocument();
  });
});
