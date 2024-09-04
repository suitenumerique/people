import { useMutation, useQueryClient } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { MailDomain } from '@/features/mail-domains';

import { KEY_LIST_MAIL_DOMAIN } from './useMailDomains';

export interface AddMailDomainParams {
  name: string;
}

export const addMailDomain = async (
  name: AddMailDomainParams['name'],
): Promise<MailDomain> => {
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

export const useAddMailDomain = ({
  onSuccess,
  onError,
}: {
  onSuccess: (data: MailDomain) => void;
  onError: (error: APIError) => void;
}) => {
  const queryClient = useQueryClient();
  return useMutation<MailDomain, APIError, string>({
    mutationFn: addMailDomain,
    onSuccess: (data) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN],
      });
      onSuccess(data);
    },
    onError: (error) => {
      onError(error);
    },
  });
};
