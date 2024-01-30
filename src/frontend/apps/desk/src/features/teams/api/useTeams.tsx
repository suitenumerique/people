import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIList, fetchAPI } from '@/api';

interface TeamResponse {
  id: string;
  name: string;
}

type TeamsResponse = APIList<TeamResponse>;
export interface TeamsResponseError {
  detail: string;
}

export const getTeams = async () => {
  const response = await fetchAPI(`teams/`);

  if (!response.ok) {
    throw new Error(`Couldn't fetch teams: ${response.statusText}`);
  }
  return response.json();
};

export const KEY_LIST_TEAM = 'teams';

export function useTeams(
  queryConfig?: UseQueryOptions<
    TeamsResponse,
    TeamsResponseError,
    TeamsResponse
  >,
) {
  return useQuery<TeamsResponse, TeamsResponseError, TeamsResponse>({
    queryKey: [KEY_LIST_TEAM],
    queryFn: getTeams,
    ...queryConfig,
  });
}
