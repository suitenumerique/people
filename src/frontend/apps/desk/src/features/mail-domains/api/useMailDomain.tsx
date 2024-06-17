import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { MailDomain } from '../types';

export type MailDomainParams = {
  slug: string;
};

type MailDomainResponse = MailDomain;

export const getMailDomain = async ({
  slug,
}: MailDomainParams): Promise<MailDomainResponse> => {
  const response = await fetchAPI(`mail-domains/${slug}`);

  if (!response.ok) {
    throw new APIError(
      `Failed to get the mail domain ${slug}`,
      await errorCauses(response),
    );
  }

  return response.json() as Promise<MailDomainResponse>;
};

const KEY_MAIL_DOMAIN = 'mail-domain';

export function useMailDomain(
  param: MailDomainParams,
  queryConfig?: UseQueryOptions<
    MailDomainResponse,
    APIError,
    MailDomainResponse
  >,
) {
  return useQuery<MailDomainResponse, APIError, MailDomainResponse>({
    queryKey: [KEY_MAIL_DOMAIN, param],
    queryFn: () => getMailDomain(param),
    ...queryConfig,
  });
}
