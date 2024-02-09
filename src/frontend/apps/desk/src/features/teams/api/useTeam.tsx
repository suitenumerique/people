import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { fetchAPI } from '@/api';

import { TeamResponse } from './types';

export type TeamParams = {
  id: string;
};

export interface TeamResponseError {
  detail?: string;
  status?: number;
  cause?: string;
}

export const getTeam = async ({ id }: TeamParams): Promise<TeamResponse> => {
  const response = await fetchAPI(`teams/${id}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw {
        status: 404,
        message: `Team with id ${id} not found`,
      };
    }

    throw new Error(`Couldn't fetch team:`, {
      cause: ((await response.json()) as TeamResponseError).detail,
    });
  }
  return response.json() as Promise<TeamResponse>;
};

export const KEY_TEAM = 'team';

export function useTeam(
  param: TeamParams,
  queryConfig?: UseQueryOptions<TeamResponse, TeamResponseError, TeamResponse>,
) {
  return useQuery<TeamResponse, TeamResponseError, TeamResponse>({
    queryKey: [KEY_TEAM, param],
    queryFn: () => getTeam(param),
    ...queryConfig,
  });
}
