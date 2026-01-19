import { useInfiniteQuery } from '@tanstack/react-query';

import { KEY_LIST_ALIAS, getMailDomainAliases } from './useAliases';

export type MailDomainAliasesInfiniteParams = {
  mailDomainSlug: string;
  ordering?: string;
};

export function useAliasesInfinite(
  param: MailDomainAliasesInfiniteParams,
  queryConfig = {},
) {
  return useInfiniteQuery({
    initialPageParam: 1,
    queryKey: [KEY_LIST_ALIAS, param],
    queryFn: ({ pageParam }) =>
      getMailDomainAliases({
        mailDomainSlug: param.mailDomainSlug,
        page: pageParam,
        ordering: param.ordering,
      }),
    getNextPageParam(lastPage, allPages) {
      // When there is no more page, return undefined
      if (!lastPage.next) {
        return undefined;
      }
      return allPages.length + 1;
    },
    ...queryConfig,
  });
}
