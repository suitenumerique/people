import {
  DefinedInitialDataInfiniteOptions,
  InfiniteData,
  QueryKey,
  useInfiniteQuery,
} from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';

import { MailDomain } from '../types';

type MailDomainsResponse = APIList<MailDomain>;

export enum EnumMailDomainsOrdering {
  BY_CREATED_AT = 'created_at',
  BY_CREATED_AT_DESC = '-created_at',
}

export type MailDomainsParams = {
  ordering?: string | EnumMailDomainsOrdering;
};

type MailDomainsAPIParams = MailDomainsParams & {
  page: number;
};

export const getMailDomains = async ({
  ordering,
  page,
}: MailDomainsAPIParams): Promise<MailDomainsResponse> => {
  const orderingQuery = ordering ? `&ordering=${ordering}` : '';
  const response = await fetchAPI(`mail-domains/?page=${page}${orderingQuery}`);

  if (!response.ok) {
    throw new APIError(
      'Failed to get the mail domains',
      await errorCauses(response),
    );
  }

  return response.json() as Promise<MailDomainsResponse>;
};

export const KEY_LIST_MAIL_DOMAIN = 'mail-domains';

export function useMailDomains(
  param: MailDomainsParams,
  queryConfig?: DefinedInitialDataInfiniteOptions<
    MailDomainsResponse,
    APIError,
    InfiniteData<MailDomainsResponse>,
    QueryKey,
    number
  >,
) {
  return useInfiniteQuery<
    MailDomainsResponse,
    APIError,
    InfiniteData<MailDomainsResponse>,
    QueryKey,
    number
  >({
    initialPageParam: 1,
    queryKey: [KEY_LIST_MAIL_DOMAIN, param],
    queryFn: ({ pageParam }) => getMailDomains({ ...param, page: pageParam }),
    getNextPageParam(lastPage, allPages) {
      return lastPage.next ? allPages.length + 1 : undefined;
    },
    retry: 0,
    ...queryConfig,
  });
}
