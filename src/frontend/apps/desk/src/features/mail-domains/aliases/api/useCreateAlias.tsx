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
  const {
    onSuccess: optionsOnSuccess,
    onError: optionsOnError,
    ...restOptions
  } = options;
  return useMutation<void, APIError, CreateAliasParams>({
    mutationFn: createAlias,
    ...restOptions,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [
          KEY_LIST_ALIAS,
          { mailDomainSlug: variables.mailDomainSlug },
        ],
      });
      if (optionsOnSuccess) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          optionsOnSuccess as unknown as (
            data: void,
            variables: CreateAliasParams,
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
            variables: CreateAliasParams,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
