import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';

import { MailDomainMailbox } from '../types';

export type MailDomainMailboxesParams = {
  mailDomainSlug: string;
  page: number;
  ordering?: string;
};

type MailDomainMailboxesResponse = APIList<MailDomainMailbox>;

export const getMailDomainMailboxes = async ({
  mailDomainSlug,
  page,
  ordering,
}: MailDomainMailboxesParams): Promise<MailDomainMailboxesResponse> => {
  let url = `mail-domains/${mailDomainSlug}/mailboxes/?page=${page}`;

  if (ordering) {
    url += '&ordering=' + ordering;
  }

  const response = await fetchAPI(url);

  if (!response.ok) {
    throw new APIError(
      `Failed to get the mailboxes of mail domain ${mailDomainSlug}`,
      await errorCauses(response),
    );
  }

  return response.json() as Promise<MailDomainMailboxesResponse>;
};

export const KEY_LIST_MAILBOX = 'mailboxes';

export function useMailboxes(
  param: MailDomainMailboxesParams,
  queryConfig?: UseQueryOptions<
    MailDomainMailboxesResponse,
    APIError,
    MailDomainMailboxesResponse
  >,
) {
  return useQuery<
    MailDomainMailboxesResponse,
    APIError,
    MailDomainMailboxesResponse
  >({
    queryKey: [KEY_LIST_MAILBOX, param],
    queryFn: () => getMailDomainMailboxes(param),
    ...queryConfig,
  });
}
