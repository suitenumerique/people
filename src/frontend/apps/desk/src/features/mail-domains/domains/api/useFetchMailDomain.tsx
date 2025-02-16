import { useMutation } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { MailDomain } from '../types';

export const fetchMailDomain = async (slug: string): Promise<MailDomain> => {
  const response = await fetchAPI(`mail-domains/${slug}/fetch/`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new APIError(
      'Failed to fetch domain from Dimail',
      await errorCauses(response),
    );
  }

  return response.json() as Promise<MailDomain>;
};

export const useFetchFromDimail = ({
  onSuccess,
  onError,
}: {
  onSuccess: (data: MailDomain) => void;
  onError: (error: APIError) => void;
}) => {
  return useMutation<MailDomain, APIError, string>({
    mutationFn: fetchMailDomain,
    onSuccess: (data) => {
      onSuccess(data);
    },
    onError: (error) => {
      onError(error);
    },
  });
};
