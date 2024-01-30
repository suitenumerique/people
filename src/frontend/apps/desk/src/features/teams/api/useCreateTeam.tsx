import { useMutation, useQueryClient } from '@tanstack/react-query';

import { fetchAPI } from '@/api';

import { KEY_LIST_TEAM } from './useTeams';

type CreateTeamResponse = {
  id: string;
  name: string;
};
export interface CreateTeamResponseError {
  detail: string;
}

export const createTeam = async (name: string) => {
  const response = await fetchAPI(`teams/`, {
    method: 'POST',
    body: JSON.stringify({
      name,
    }),
  });

  if (!response.ok) {
    throw new Error(`Couldn't create team: ${response.statusText}`);
  }

  return response.json();
};

export function useCreateTeam() {
  const queryClient = useQueryClient();
  return useMutation<CreateTeamResponse, CreateTeamResponseError, string>({
    mutationFn: createTeam,
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_TEAM],
        exact: true,
      });
    },
  });
}
