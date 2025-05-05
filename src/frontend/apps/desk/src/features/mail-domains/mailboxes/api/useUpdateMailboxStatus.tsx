import { useMutation, useQueryClient } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_MAILBOX } from './useMailboxes';

export interface DisableMailboxParams {
  mailDomainSlug: string;
  mailboxId: string;
  isEnabled: boolean;
}

export interface ResetPasswordParams {
  mailDomainSlug: string;
  mailboxId: string;
}

export const resetPassword = async ({
  mailDomainSlug,
  mailboxId,
}: ResetPasswordParams): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/mailboxes/${mailboxId}/reset/`,
    {
      method: 'POST',
    },
  );

  if (!response.ok) {
    throw new APIError(
      'Failed to reset mailbox password',
      await errorCauses(response),
    );
  }
};

export const disableMailbox = async ({
  mailDomainSlug,
  mailboxId,
  isEnabled,
}: DisableMailboxParams): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/mailboxes/${mailboxId}/${
      isEnabled ? 'enable' : 'disable'
    }/`,
    {
      method: 'POST',
    },
  );

  if (!response.ok) {
    throw new APIError(
      'Failed to disable the mailbox',
      await errorCauses(response),
    );
  }
};


export const useUpdateMailboxStatus = () => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, DisableMailboxParams>({
    mutationFn: disableMailbox,
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          KEY_LIST_MAILBOX,
          { mailDomainSlug: variables.mailDomainSlug },
        ],
      });
    },
  });
};
