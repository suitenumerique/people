import { useMutation, useQueryClient } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { MailDomain } from '../types';

import { KEY_LIST_MAIL_DOMAIN } from './useMailDomains';

export interface AddMailDomainParams {
  name: string;
  supportEmail: string;
}

export const addMailDomain = async ({
  name,
  supportEmail,
}: AddMailDomainParams): Promise<MailDomain> => {
  const response = await fetchAPI(`mail-domains/`, {
    method: 'POST',
    body: JSON.stringify({ name, support_email: supportEmail }),
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
  return useMutation<MailDomain, APIError, AddMailDomainParams>({
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
