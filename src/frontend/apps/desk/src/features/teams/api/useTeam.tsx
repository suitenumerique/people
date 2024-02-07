import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { fetchAPI } from '@/api';

import { TeamResponse } from './types';

export type TeamParams = {
  id: string;
};

export interface TeamResponseError {
  detail: string;
}

export const getTeam = async ({ id }: TeamParams): Promise<TeamResponse> => {
  const response = await fetchAPI(`teams/${id}`);

  if (!response.ok) {
    throw new Error(`Couldn't fetch team: ${response.statusText}`);
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
