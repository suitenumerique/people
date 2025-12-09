import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_ALIAS } from './useAliases';

export interface UpdateAliasParams {
  id: string;
  localPart: string;
  destination: string;
  mailDomainSlug: string;
}

export const updateAlias = async ({
  mailDomainSlug,
  id,
  localPart,
  destination,
}: UpdateAliasParams): Promise<void> => {
  // Use local_part in URL (lookup_field), but identify by id in the body
  const response = await fetchAPI(`mail-domains/${mailDomainSlug}/aliases/${localPart}/`, {
    method: 'PATCH',
    body: JSON.stringify({ id, destination }),
  });

  if (!response.ok) {
    const errorData = await errorCauses(response);
    throw new APIError('Failed to update the alias', {
      status: errorData.status,
      cause: errorData.cause as string[],
      data: errorData.data,
    });
  }
};

type UseUpdateAliasParams = { mailDomainSlug: string } & UseMutationOptions<
  void,
  APIError,
  UpdateAliasParams
>;

export const useUpdateAlias = (options: UseUpdateAliasParams) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, UpdateAliasParams>({
    mutationFn: updateAlias,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [
          KEY_LIST_ALIAS,
          { mailDomainSlug: variables.mailDomainSlug },
        ],
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

