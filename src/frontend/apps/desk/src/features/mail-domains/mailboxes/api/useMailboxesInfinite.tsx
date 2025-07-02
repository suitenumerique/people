import { useInfiniteQuery } from '@tanstack/react-query';

import { APIError, APIList } from '@/api';

import { MailDomainMailbox } from '../types';

import {
  KEY_LIST_MAILBOX,
  MailDomainMailboxesParams,
  getMailDomainMailboxes,
} from './useMailboxes';

// Redéfinition locale du type
type MailDomainMailboxesResponse = APIList<MailDomainMailbox>;

export function useMailboxesInfinite(
  param: Omit<MailDomainMailboxesParams, 'page'>,
  queryConfig = {},
) {
  return useInfiniteQuery<
    MailDomainMailboxesResponse,
    APIError,
    MailDomainMailboxesResponse,
    [string, Omit<MailDomainMailboxesParams, 'page'>],
    number
  >({
    queryKey: [KEY_LIST_MAILBOX, param],
    queryFn: ({ pageParam = 1 }) =>
      getMailDomainMailboxes({ ...param, page: pageParam }),
    getNextPageParam: (lastPage): number | undefined => {
      if (!lastPage.next) {
        return undefined;
      }
      try {
        const url = new URL(lastPage.next, window.location.origin);
        const nextPage = url.searchParams.get('page');
        return nextPage ? Number(nextPage) : undefined;
      } catch {
        return undefined;
      }
    },
    initialPageParam: 1,
    ...queryConfig,
  });
}
