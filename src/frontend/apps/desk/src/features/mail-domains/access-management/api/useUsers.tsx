import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { User } from '@/core/auth';
import { MailDomain } from '@/features/mail-domains/domains/types';

export type UsersParams = {
  query: string;
  mailDomain: MailDomain['slug'];
};

type UsersResponse = User[];

export const getUsers = async ({
  query,
  mailDomain,
}: UsersParams): Promise<UsersResponse> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomain}/accesses/users/?q=${query}`,
  );

  if (!response.ok) {
    throw new APIError('Failed to get the users', await errorCauses(response));
  }

  const res = (await response.json()) as User[];
  return res;
};

export const KEY_LIST_USER = 'users';

export function useUsers(
  param: UsersParams,
  queryConfig?: UseQueryOptions<UsersResponse, APIError, UsersResponse>,
) {
  return useQuery<UsersResponse, APIError, UsersResponse>({
    queryKey: [KEY_LIST_USER, param],
    queryFn: () => getUsers(param),
    ...queryConfig,
  });
}
