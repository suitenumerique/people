import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { KEY_MAIL_DOMAIN, Role } from '@/features/mail-domains/domains';

import { Access } from '../types';

import { KEY_LIST_MAIL_DOMAIN_ACCESSES } from './useMailDomainAccesses';

interface UpdateMailDomainAccessProps {
  slug: string;
  accessId: string;
  role: Role;
}

export const updateMailDomainAccess = async ({
  slug,
  accessId,
  role,
}: UpdateMailDomainAccessProps): Promise<Access> => {
  const response = await fetchAPI(
    `mail-domains/${slug}/accesses/${accessId}/`,
    {
      method: 'PATCH',
      body: JSON.stringify({
        role,
      }),
    },
  );

  if (!response.ok) {
    throw new APIError('Failed to update role', await errorCauses(response));
  }

  return response.json() as Promise<Access>;
};

type UseUpdateMailDomainAccess = Partial<Access>;

type UseUpdateMailDomainAccessOptions = UseMutationOptions<
  Access,
  APIError,
  UseUpdateMailDomainAccess
>;

export const useUpdateMailDomainAccess = (
  options?: UseUpdateMailDomainAccessOptions,
) => {
  const queryClient = useQueryClient();
  return useMutation<Access, APIError, UpdateMailDomainAccessProps>({
    mutationFn: updateMailDomainAccess,
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN_ACCESSES],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_MAIL_DOMAIN],
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
