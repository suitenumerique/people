import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';
import { User } from '@/core/auth';
import { MailDomain } from '@/features/mail-domains/domains/types';

export type UsersParams = {
  query: string;
  mailDomain: MailDomain['slug'];
};

type UsersResponse = APIList<User>;

export const getUsers = async ({
  query,
  mailDomain,
}: UsersParams): Promise<UsersResponse> => {
  const queriesParams = [];
  queriesParams.push(query ? `q=${query}` : '');

  const response = await fetchAPI(`mail-domains/${mailDomain}/accesses/users/?${queriesParams}`);

  if (!response.ok) {
    throw new APIError('Failed to get the users', await errorCauses(response));
  }

  return response.json() as Promise<UsersResponse>;
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
