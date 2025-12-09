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
  localPart: string; // Still needed for URL construction
}

export const deleteAliasById = async ({
  mailDomainSlug,
  aliasId,
  localPart,
}: DeleteAliasByIdParams): Promise<void> => {
  // Use localPart in URL but identify by id in request
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/aliases/${localPart}/`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id: aliasId }),
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
  });
};

