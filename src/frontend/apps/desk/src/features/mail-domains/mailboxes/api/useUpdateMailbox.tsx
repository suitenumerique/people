import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_MAILBOX } from './useMailboxes';

export interface UpdateMailboxParams {
  first_name: string;
  last_name: string;
  secondary_email: string;
  mailDomainSlug: string;
}

export const updateMailbox = async ({
  mailDomainSlug,
  mailboxId,
  ...data
}: UpdateMailboxParams & { mailboxId: string }): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/mailboxes/${mailboxId}/`,
    {
      method: 'PATCH',
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    const errorData = await errorCauses(response);
    console.log('Error data:', errorData);
    throw new APIError('Failed to update the mailbox', {
      status: errorData.status,
      cause: errorData.cause as string[],
      data: errorData.data,
    });
  }
};

type UseUpdateMailboxParams = {
  mailDomainSlug: string;
  mailboxId: string;
} & UseMutationOptions<void, APIError, UpdateMailboxParams>;

export const useUpdateMailbox = (options: UseUpdateMailboxParams) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, UpdateMailboxParams>({
    mutationFn: (data) =>
      updateMailbox({ ...data, mailboxId: options.mailboxId }),
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
            variables: UpdateMailboxParams,
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
            variables: UpdateMailboxParams,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
