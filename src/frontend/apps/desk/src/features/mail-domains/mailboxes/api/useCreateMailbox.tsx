import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_MAILBOX } from './useMailboxes';

export interface CreateMailboxParams {
  first_name: string;
  last_name: string;
  local_part: string;
  secondary_email: string;
  mailDomainSlug: string;
}

export const createMailbox = async ({
  mailDomainSlug,
  ...data
}: CreateMailboxParams): Promise<void> => {
  const response = await fetchAPI(`mail-domains/${mailDomainSlug}/mailboxes/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await errorCauses(response);
    console.log('Error data:', errorData);
    throw new APIError('Failed to create the mailbox', {
      status: errorData.status,
      cause: errorData.cause as string[],
      data: errorData.data,
    });
  }
};

type UseCreateMailboxParams = { mailDomainSlug: string } & UseMutationOptions<
  void,
  APIError,
  CreateMailboxParams
>;

export const useCreateMailbox = (options: UseCreateMailboxParams) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, CreateMailboxParams>({
    mutationFn: createMailbox,
    ...options,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [
          KEY_LIST_MAILBOX,
          { mailDomainSlug: variables.mailDomainSlug },
        ],
      });
      if (options?.onSuccess) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          options.onSuccess as unknown as (
            data: void,
            variables: CreateMailboxParams,
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
            variables: CreateMailboxParams,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
