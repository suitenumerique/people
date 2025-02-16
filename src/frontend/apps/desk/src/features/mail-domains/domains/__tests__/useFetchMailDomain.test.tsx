import fetchMock from 'fetch-mock';

import { APIError } from '@/api';
import { fetchMailDomain } from '@/features/mail-domains/domains/api/useFetchMailDomain';
import { MailDomain } from '@/features/mail-domains/domains/types';

const mockMailDomain: MailDomain = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'example.com',
  status: 'enabled',
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
    mx: 'Je veux que le MX du domaine soit mx.ox.numerique.gouv.fr.',
  },
  expected_config: [
    { target: '', type: 'mx', value: 'mx.ox.numerique.gouv.fr.' },
    {
      target: 'dimail._domainkey',
      type: 'txt',
      value: 'v=DKIM1; h=sha256; k=rsa; p=X...X',
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

describe('fetchMailDomain', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('fetch the domain successfully', async () => {
    fetchMock.postOnce('end:/mail-domains/example-slug/fetch/', {
      status: 200,
      body: mockMailDomain,
    });

    const result = await fetchMailDomain('example-slug');

    expect(result).toEqual(mockMailDomain);
    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastUrl()).toContain('/mail-domains/example-slug/fetch/');
  });

  it('throw an error when the domain is not found', async () => {
    fetchMock.postOnce('end:/mail-domains/example-slug/fetch/', {
      status: 404,
      body: { cause: ['Domain not found'] },
    });

    await expect(fetchMailDomain('example-slug')).rejects.toThrow(APIError);
    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastUrl()).toContain('/mail-domains/example-slug/fetch/');
  });
});
