import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { TeamResponse } from './types';

export type TeamParams = {
  id: string;
};

export const getTeam = async ({ id }: TeamParams): Promise<TeamResponse> => {
  const response = await fetchAPI(`teams/${id}`);

  if (!response.ok) {
    throw new APIError('Failed to get the team', await errorCauses(response));
  }

  return response.json() as Promise<TeamResponse>;
};

export const KEY_TEAM = 'team';

export function useTeam(
  param: TeamParams,
  queryConfig?: UseQueryOptions<TeamResponse, APIError, TeamResponse>,
) {
  return useQuery<TeamResponse, APIError, TeamResponse>({
    queryKey: [KEY_TEAM, param],
    queryFn: () => getTeam(param),
    ...queryConfig,
  });
}
