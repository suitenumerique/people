import { useMutation, useQueryClient } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { MailDomain } from '@/features/mail-domains';

import { KEY_LIST_MAIL_DOMAIN } from './useMailDomains';

export const createMailDomain = async (name: string): Promise<MailDomain> => {
  const response = await fetchAPI(`mail-domains/`, {
    method: 'POST',
    body: JSON.stringify({
      name,
    }),
  });

  if (!response.ok) {
    throw new APIError(
      'Failed to add the mail domain',
      await errorCauses(response),
    );
  }

  return response.json() as Promise<MailDomain>;
};

export function useCreateMailDomain({
  onSuccess,
}: {
  onSuccess: (data: MailDomain) => void;
}) {
  const queryClient = useQueryClient();
  return useMutation<MailDomain, APIError, string>({
    mutationFn: createMailDomain,
    onSuccess: (data) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN],
      });
      onSuccess(data);
    },
  });
}
