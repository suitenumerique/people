import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';

import { Access } from '../types';

export type TeamAccessesAPIParams = {
  page: number;
  teamId: string;
  ordering?: string;
  query?: string;
};

type AccessesResponse = APIList<Access>;

/**
 * @description Since there cannot be both a page and q params in query params at the same time, the queryString
 * building order should not be changed.
 * @param page
 * @param teamId
 * @param ordering
 * @param q
 */
export const getTeamAccesses = async ({
  page,
  teamId,
  ordering,
  query,
}: TeamAccessesAPIParams): Promise<AccessesResponse> => {
  const url = `teams/${teamId}/accesses/`;

  let queryString = '';

  if (page) {
    queryString = `?page=${page}`;
  }

  if (query) {
    queryString = `?q=${query}`;
  }

  if (ordering) {
    queryString += `&ordering=${ordering}`;
  }

  const response = await fetchAPI(`${url}${queryString}`);

  if (!response.ok) {
    throw new APIError(
      'Failed to get the team accesses',
      await errorCauses(response),
    );
  }

  return response.json() as Promise<AccessesResponse>;
};

export const KEY_LIST_TEAM_ACCESSES = 'teams-accesses';

export function useTeamAccesses(
  params: TeamAccessesAPIParams,
  queryConfig?: UseQueryOptions<AccessesResponse, APIError, AccessesResponse>,
) {
  return useQuery<AccessesResponse, APIError, AccessesResponse>({
    queryKey: [KEY_LIST_TEAM_ACCESSES, params],
    queryFn: () => getTeamAccesses(params),
    ...queryConfig,
  });
}
