import { render, screen, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';
import { useRouter as useNavigate } from 'next/navigation';
import { useRouter } from 'next/router';

import { AccessesContent } from '@/features/mail-domains/access-management';
import { Role } from '@/features/mail-domains/domains';
import MailDomainAccessesPage from '@/pages/mail-domains/[slug]/accesses';
import { AppWrapper } from '@/tests/utils';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

jest.mock(
  '@/features/mail-domains/access-management/components/AccessesContent',
  () => ({
    AccessesContent: jest.fn(() => <div>AccessContent</div>),
  }),
);

describe('MailDomainAccessesPage', () => {
  const mockRouterReplace = jest.fn();
  const mockNavigate = { replace: mockRouterReplace };
  const mockRouter = {
    query: { slug: 'example-slug' },
  };

  (useRouter as jest.Mock).mockReturnValue(mockRouter);
  (useNavigate as jest.Mock).mockReturnValue(mockNavigate);

  beforeEach(() => {
    jest.clearAllMocks();
    fetchMock.reset();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);
  });

  afterEach(() => {
    fetchMock.restore();
  });

  const renderPage = () => {
    render(<MailDomainAccessesPage />, { wrapper: AppWrapper });
  };

  it('renders loader while loading', () => {
    // Simulate a never-resolving promise to mock loading
    fetchMock.mock(
      `end:/mail-domains/${mockRouter.query.slug}/`,
      new Promise(() => {}),
    );

    renderPage();

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders error message when there is an error', async () => {
    fetchMock.mock(`end:/mail-domains/${mockRouter.query.slug}/`, {
      status: 500,
    });

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText('Something bad happens, please retry.'),
      ).toBeInTheDocument();
    });
  });

  it('redirects to 404 page if the domain is not found', async () => {
    fetchMock.mock(
      `end:/mail-domains/${mockRouter.query.slug}/`,
      {
        body: { detail: 'Not found' },
        status: 404,
      },
      { overwriteRoutes: true },
    );

    renderPage();

    await waitFor(() => {
      expect(mockRouterReplace).toHaveBeenCalledWith('/404');
    });
  });

  it('renders the AccessesContent when data is available', async () => {
    const mockMailDomain = {
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

    fetchMock.mock(`end:/mail-domains/${mockRouter.query.slug}/`, {
      body: mockMailDomain,
      status: 200,
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText('AccessContent')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(AccessesContent).toHaveBeenCalledWith(
        {
          mailDomain: mockMailDomain,
          currentRole: Role.OWNER,
        },
        undefined, // adding this undefined value is necessary to load jest context
      );
    });
  });

  it('throws an error when slug is invalid', () => {
    console.error = jest.fn(); // Suppress expected error in jest logs

    (useRouter as jest.Mock).mockReturnValue({
      query: { slug: ['invalid-array-slug-in-array'] },
    });

    expect(() => renderPage()).toThrow('Invalid mail domain slug');
  });
});
