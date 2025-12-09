import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_ALIAS } from './useAliases';

export interface CreateAliasParams {
  local_part: string;
  destination: string;
  mailDomainSlug: string;
}

export const createAlias = async ({
  mailDomainSlug,
  ...data
}: CreateAliasParams): Promise<void> => {
  const response = await fetchAPI(`mail-domains/${mailDomainSlug}/aliases/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await errorCauses(response);
    throw new APIError('Failed to create the alias', {
      status: errorData.status,
      cause: errorData.cause as string[],
      data: errorData.data,
    });
  }
};

type UseCreateAliasParams = { mailDomainSlug: string } & UseMutationOptions<
  void,
  APIError,
  CreateAliasParams
>;

export const useCreateAlias = (options: UseCreateAliasParams) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, CreateAliasParams>({
    mutationFn: createAlias,
    onSuccess: (data, variables, onMutateResult, context) => {
      void queryClient.invalidateQueries({
        queryKey: [
          KEY_LIST_ALIAS,
          { mailDomainSlug: variables.mailDomainSlug },
        ],
      });
      if (options?.onSuccess) {
        options.onSuccess(data, variables, onMutateResult, context);
      }
    },
    onError: (error, variables, onMutateResult, context) => {
      if (options?.onError) {
        options.onError(error, variables, onMutateResult, context);
      }
    },
  });
};


