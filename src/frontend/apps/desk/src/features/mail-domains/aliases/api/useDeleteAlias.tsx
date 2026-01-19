import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_ALIAS } from './useAliases';

interface DeleteAliasParams {
  mailDomainSlug: string;
  localPart: string;
}

export const deleteAlias = async ({
  mailDomainSlug,
  localPart,
}: DeleteAliasParams): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/aliases/delete/?local_part=${encodeURIComponent(localPart)}`,
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

type UseDeleteAliasOptions = UseMutationOptions<
  void,
  APIError,
  DeleteAliasParams
>;

export const useDeleteAlias = (options?: UseDeleteAliasOptions) => {
  const queryClient = useQueryClient();
  const {
    onSuccess: optionsOnSuccess,
    onError: optionsOnError,
    ...restOptions
  } = options || {};
  return useMutation<void, APIError, DeleteAliasParams>({
    mutationFn: deleteAlias,
    ...restOptions,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_ALIAS],
      });
      if (optionsOnSuccess) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          optionsOnSuccess as unknown as (
            data: void,
            variables: DeleteAliasParams,
            context: unknown,
          ) => void
        )(data, variables, context);
      }
    },
    onError: (error, variables, context) => {
      if (optionsOnError) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          optionsOnError as unknown as (
            error: APIError,
            variables: DeleteAliasParams,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
