import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { KEY_MAIL_DOMAIN, Role } from '@/features/mail-domains/domains';

import { Access } from '../types';

import { KEY_LIST_MAIL_DOMAIN_ACCESSES } from './useMailDomainAccesses';

interface CreateMailDomainAccessProps {
  slug: string;
  user: string;
  role: Role;
}

export const createMailDomainAccess = async ({
  slug,
  user,
  role,
}: CreateMailDomainAccessProps): Promise<Access> => {
  const response = await fetchAPI(`mail-domains/${slug}/accesses/`, {
    method: 'POST',
    body: JSON.stringify({ user, role }),
  });

  if (!response.ok) {
    throw new APIError('Failed to create role', await errorCauses(response));
  }

  return response.json() as Promise<Access>;
};

type UseCreateMailDomainAccessOptions = UseMutationOptions<
  Access,
  APIError,
  CreateMailDomainAccessProps
>;

export const useCreateMailDomainAccess = (
  options?: UseCreateMailDomainAccessOptions,
) => {
  const queryClient = useQueryClient();

  return useMutation<Access, APIError, CreateMailDomainAccessProps>({
    mutationFn: createMailDomainAccess,
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN_ACCESSES],
      });
      void queryClient.invalidateQueries({ queryKey: [KEY_MAIL_DOMAIN] });
      options?.onSuccess?.(data, variables, onMutateResult, context);
    },
    onError: (error, variables, onMutateResult, context) => {
      options?.onError?.(error, variables, onMutateResult, context);
    },
  });
};
