import { fireEvent, render, screen } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { MailDomain } from '@/features/mail-domains/domains';
import { AppWrapper } from '@/tests/utils';

import { MailDomainView } from '../components/MailDomainView';

const toast = jest.fn();
jest.mock('@openfun/cunningham-react', () => ({
  ...jest.requireActual('@openfun/cunningham-react'),
  useToastProvider: () => ({
    toast,
  }),
}));

const mockMailDomain: MailDomain = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'example.com',
  status: 'action_required',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  slug: 'example-com',
  support_email: 'support@example.com',
  abilities: {
    delete: false,
    manage_accesses: true,
    get: true,
    patch: true,
    put: true,
    post: true,
  },
  action_required_details: {
    mx: 'Je veux que le MX du domaine soit mx.ox.numerique.gouv.fr....',
  },
  expected_config: [
    { target: '', type: 'mx', value: 'mx.ox.numerique.gouv.fr.' },
    {
      target: 'dimail._domainkey',
      type: 'txt',
      value:
        'v=DKIM1; h=sha256; k=rsa; p=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    },
    { target: 'imap', type: 'cname', value: 'imap.ox.numerique.gouv.fr.' },
    { target: 'smtp', type: 'cname', value: 'smtp.ox.numerique.gouv.fr.' },
    {
      target: '',
      type: 'txt',
      value: 'v=spf1 include:_spf.ox.numerique.gouv.fr -all',
    },
    {
      target: 'webmail',
      type: 'cname',
      value: 'webmail.ox.numerique.gouv.fr.',
    },
  ],
};

describe('<MailDomainView />', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    fetchMock.restore();
  });
  it('display action required button and open modal with information when domain status is action_required', () => {
    render(<MailDomainView mailDomain={mockMailDomain} />, {
      wrapper: AppWrapper,
    });
    // Check if action required button is displayed
    const actionButton = screen.getByText('Actions required');
    expect(actionButton).toBeInTheDocument();

    // Click the button and verify modal content
    fireEvent.click(actionButton);

    // Verify modal title and content
    expect(screen.getByText('Required actions on domain')).toBeInTheDocument();
    expect(
      screen.getByText(
        /Je veux que le MX du domaine soit mx.ox.numerique.gouv.fr/,
      ),
    ).toBeInTheDocument();

    // Verify DNS configuration section
    expect(
      screen.getByText(/DNS Configuration Required:/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/imap.ox.numerique.gouv.fr./i)).toBeInTheDocument();
    expect(
      screen.getByText(/webmail.ox.numerique.gouv.fr./i),
    ).toBeInTheDocument();
  });
});
