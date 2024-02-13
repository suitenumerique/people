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

export const createTeam = async (name: string): Promise<CreateTeamResponse> => {
  const response = await fetchAPI(`teams/`, {
    method: 'POST',
    body: JSON.stringify({
      name,
    }),
  });

  if (!response.ok) {
    throw new Error(`Couldn't create team: ${response.statusText}`);
  }

  return response.json() as Promise<CreateTeamResponse>;
};

interface CreateTeamProps {
  onSuccess: (data: CreateTeamResponse) => void;
}

export function useCreateTeam({ onSuccess }: CreateTeamProps) {
  const queryClient = useQueryClient();
  return useMutation<CreateTeamResponse, CreateTeamResponseError, string>({
    mutationFn: createTeam,
    onSuccess: (data) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_TEAM],
      });
      onSuccess(data);
    },
  });
}
