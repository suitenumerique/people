import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_TEAM } from './useTeams';

interface RemoveTeamProps {
  teamId: string;
}

export const removeTeam = async ({
  teamId,
}: RemoveTeamProps): Promise<void> => {
  const response = await fetchAPI(`teams/${teamId}/`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new APIError(
      'Failed to delete the team',
      await errorCauses(response),
    );
  }
};

type UseRemoveTeamOptions = UseMutationOptions<void, APIError, RemoveTeamProps>;

export const useRemoveTeam = (options?: UseRemoveTeamOptions) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, RemoveTeamProps>({
    mutationFn: removeTeam,
    ...options,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_TEAM],
      });
      if (options?.onSuccess) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          options.onSuccess as unknown as (
            data: void,
            variables: RemoveTeamProps,
            context: unknown,
          ) => void
        )(data, variables, context);
      }
    },
    onError: (error, variables, context) => {
      if (options?.onError) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          options.onError as unknown as (
            error: APIError,
            variables: RemoveTeamProps,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
