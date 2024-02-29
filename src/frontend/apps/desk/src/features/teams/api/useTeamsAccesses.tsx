import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';

import { PAGE_SIZE } from '../conf';

import { dummyDataAPITeamAccesses } from './data/teams';
import { Access } from './types';

export type TeamAccessesAPIParams = {
  page: number;
  teamId: string;
};

type AccessesResponse = APIList<Access>;

export const getTeamAccesses = async ({
  page,
  teamId,
}: TeamAccessesAPIParams): Promise<AccessesResponse> => {
  /**
   * TODO: Remove this block when the API endpoint is ready
   */
  return await new Promise((resolve) => {
    setTimeout(() => {
      resolve(dummyDataAPITeamAccesses(100, PAGE_SIZE));
    }, 500);
  });

  const response = await fetchAPI(`teams/${teamId}/accesses/?page=${page}`);

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
