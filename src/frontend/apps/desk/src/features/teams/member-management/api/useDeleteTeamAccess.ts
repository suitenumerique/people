import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { KEY_LIST_TEAM, KEY_TEAM } from '@/features/teams/team-management';

import { KEY_LIST_TEAM_ACCESSES } from './useTeamsAccesses';

interface DeleteTeamAccessProps {
  teamId: string;
  accessId: string;
}

export const deleteTeamAccess = async ({
  teamId,
  accessId,
}: DeleteTeamAccessProps): Promise<void> => {
  const response = await fetchAPI(`teams/${teamId}/accesses/${accessId}/`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new APIError(
      'Failed to delete the member',
      await errorCauses(response),
    );
  }
};

type UseDeleteTeamAccessOptions = UseMutationOptions<
  void,
  APIError,
  DeleteTeamAccessProps
>;

export const useDeleteTeamAccess = (options?: UseDeleteTeamAccessOptions) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, DeleteTeamAccessProps>({
    mutationFn: deleteTeamAccess,
    ...options,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_TEAM_ACCESSES],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_TEAM],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_TEAM],
      });
      if (options?.onSuccess) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          options.onSuccess as unknown as (
            data: void,
            variables: DeleteTeamAccessProps,
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
            variables: DeleteTeamAccessProps,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
