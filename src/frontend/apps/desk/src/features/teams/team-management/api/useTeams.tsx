import { useQuery } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { Team } from '../types';

export enum TeamsOrdering {
  BY_CREATED_ON = 'created_at',
  BY_CREATED_ON_DESC = '-created_at',
}

export type TeamsParams = {
  ordering: TeamsOrdering;
};

type TeamsResponse = Team[];

export const getTeams = async ({
  ordering,
}: TeamsParams): Promise<TeamsResponse> => {
  const orderingQuery = ordering ? `?ordering=${ordering}` : '';
  const response = await fetchAPI(`teams/${orderingQuery}`);

  if (!response.ok) {
    throw new APIError('Failed to get the teams', await errorCauses(response));
  }

  return response.json() as Promise<TeamsResponse>;
};

export const KEY_LIST_TEAM = 'teams';

export function useTeams(params: TeamsParams) {
  return useQuery({
    queryKey: [KEY_LIST_TEAM, params],
    queryFn: () => getTeams(params),
    retry: 0,
  });
}
