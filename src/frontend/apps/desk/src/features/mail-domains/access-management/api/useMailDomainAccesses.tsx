import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';

import { Access } from '../types';

export type MailDomainAccessesAPIParams = {
  page: number;
  slug: string;
  ordering?: string;
};

type AccessesResponse = APIList<Access>;

export const getMailDomainAccesses = async ({
  page,
  slug,
  ordering,
}: MailDomainAccessesAPIParams): Promise<AccessesResponse> => {
  let url = `mail-domains/${slug}/accesses/?page=${page}`;

  if (ordering) {
    url += '&ordering=' + ordering;
  }

  const response = await fetchAPI(url);

  if (!response.ok) {
    throw new APIError(
      'Failed to get the accesses',
      await errorCauses(response),
    );
  }

  return response.json() as Promise<AccessesResponse>;
};

export const KEY_LIST_MAIL_DOMAIN_ACCESSES = 'mail-domains-accesses';

export function useMailDomainAccesses(
  params: MailDomainAccessesAPIParams,
  queryConfig?: UseQueryOptions<AccessesResponse, APIError, AccessesResponse>,
) {
  return useQuery<AccessesResponse, APIError, AccessesResponse>({
    queryKey: [KEY_LIST_MAIL_DOMAIN_ACCESSES, params],
    queryFn: () => getMailDomainAccesses(params),
    ...queryConfig,
  });
}
