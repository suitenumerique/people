import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';

import { Alias } from '../types';

export type MailDomainAliasesParams = {
  mailDomainSlug: string;
  page: number;
  ordering?: string;
};

type MailDomainAliasesResponse = APIList<Alias>;

export const getMailDomainAliases = async ({
  mailDomainSlug,
  page,
  ordering,
}: MailDomainAliasesParams): Promise<MailDomainAliasesResponse> => {
  let url = `mail-domains/${mailDomainSlug}/aliases/?page=${page}`;

  if (ordering) {
    url += '&ordering=' + ordering;
  }

  const response = await fetchAPI(url);

  if (!response.ok) {
    throw new APIError(
      `Failed to get the aliases of mail domain ${mailDomainSlug}`,
      await errorCauses(response),
    );
  }

  return response.json() as Promise<MailDomainAliasesResponse>;
};

export const KEY_LIST_ALIAS = 'aliases';

export function useAliases(
  param: MailDomainAliasesParams,
  queryConfig?: UseQueryOptions<
    MailDomainAliasesResponse,
    APIError,
    MailDomainAliasesResponse
  >,
) {
  return useQuery<
    MailDomainAliasesResponse,
    APIError,
    MailDomainAliasesResponse
  >({
    queryKey: [KEY_LIST_ALIAS, param],
    queryFn: () => getMailDomainAliases(param),
    ...queryConfig,
  });
}


