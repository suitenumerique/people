import { UseQueryOptions, useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { Team } from '../types';

export type TeamParams = {
  id: string;
};

export const getTeam = async ({ id }: TeamParams): Promise<Team> => {
  const response = await fetchAPI(`teams/${id}`);

  if (!response.ok) {
    throw new APIError('Failed to get the team', await errorCauses(response));
  }

  return response.json() as Promise<Team>;
};

export const KEY_TEAM = 'team';

export function useTeam(
  param: TeamParams,
  queryConfig?: UseQueryOptions<Team, APIError, Team>,
) {
  const router = useRouter();

  return useQuery<Team, APIError, Team>({
    queryKey: [KEY_TEAM, param],
    queryFn: async () => {
      try {
        return await getTeam(param);
      } catch (error) {
        if (error instanceof APIError && error.status === 404) {
          router.replace('/404');
        }
        throw error;
      }
    },
    ...queryConfig,
  });
}
