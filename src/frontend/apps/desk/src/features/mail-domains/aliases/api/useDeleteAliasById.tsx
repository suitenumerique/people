import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_ALIAS } from './useAliases';

interface DeleteAliasByIdParams {
  mailDomainSlug: string;
  aliasId: string;
}

export const deleteAliasById = async ({
  mailDomainSlug,
  aliasId,
}: DeleteAliasByIdParams): Promise<void> => {
  // Use aliasId (pk) directly in URL as per API lookup_field = "pk"
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/aliases/${aliasId}/`,
    {
      method: 'DELETE',
    },
  );

  if (!response.ok) {
    throw new APIError(
      'Failed to delete the alias',
      await errorCauses(response),
    );
  }
};

type UseDeleteAliasByIdOptions = UseMutationOptions<
  void,
  APIError,
  DeleteAliasByIdParams
>;

export const useDeleteAliasById = (options?: UseDeleteAliasByIdOptions) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, DeleteAliasByIdParams>({
    mutationFn: deleteAliasById,
    ...options,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_ALIAS],
      });
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
    onError: (error, variables, context) => {
      if (options?.onError) {
        options.onError(error, variables, context);
      }
    },
  });
};
