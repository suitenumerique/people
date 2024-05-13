import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { MailDomain } from '../types';

export type MailDomainParams = {
  id: string;
};

type MailDomainResponse = MailDomain;

export const getMailDomain = async ({
  id,
}: MailDomainParams): Promise<MailDomainResponse> => {
  const response = await fetchAPI(`mail-domains/${id}`);

  if (!response.ok) {
    throw new APIError(
      `Failed to get the mail domain ${id}`,
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
