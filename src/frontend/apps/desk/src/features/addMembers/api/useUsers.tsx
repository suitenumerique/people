import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';
import { User } from '@/core/auth';

export type UsersParams = {
  query: string;
};

type UsersResponse = APIList<User>;

export const getUsers = async ({
  query,
}: UsersParams): Promise<UsersResponse> => {
  const queryParam = query ? `q=${query}` : '';
  const response = await fetchAPI(`users/?${queryParam}`);

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
