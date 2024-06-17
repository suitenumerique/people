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
  phone_number: string;
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
    // TODO: extend errorCauses to return the name of the invalid field names to highlight in the form?
    throw new APIError(
      'Failed to create the mailbox',
      await errorCauses(response),
    );
  }
};

type UseCreateMailboxParams = { mailDomainSlug: string } & UseMutationOptions<
  void,
  APIError,
  CreateMailboxParams
>;

export function useCreateMailbox(options: UseCreateMailboxParams) {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, CreateMailboxParams>({
    mutationFn: createMailbox,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [
          KEY_LIST_MAILBOX,
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
}
