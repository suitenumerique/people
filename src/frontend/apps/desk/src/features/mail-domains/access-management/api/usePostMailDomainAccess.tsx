import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { KEY_MAIL_DOMAIN, Role } from '@/features/mail-domains/domains';

import { Access } from '../types';
import { KEY_LIST_MAIL_DOMAIN_ACCESSES } from './useMailDomainAccesses';

interface PostMailDomainAccessProps {
  slug: string;
  user: string;
  role: Role;
}

export const postMailDomainAccess = async ({
  slug,
  user,
  role,
}: PostMailDomainAccessProps): Promise<Access> => {
  const response = await fetchAPI(`mail-domains/${slug}/accesses/`, {
    method: 'POST',
    body: JSON.stringify({ user, role }),
  });

  if (!response.ok) {
    throw new APIError('Failed to create role', await errorCauses(response));
  }

  return response.json() as Promise<Access>;
};

type UsePostMailDomainAccessOptions = UseMutationOptions<
  Access,
  APIError,
  PostMailDomainAccessProps
>;

export const usePostMailDomainAccess = (options?: UsePostMailDomainAccessOptions) => {
  const queryClient = useQueryClient();
  
  return useMutation<Access, APIError, PostMailDomainAccessProps>({
    mutationFn: postMailDomainAccess,
    ...options,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({ queryKey: [KEY_LIST_MAIL_DOMAIN_ACCESSES] });
      void queryClient.invalidateQueries({ queryKey: [KEY_MAIL_DOMAIN] });
      options?.onSuccess?.(data, variables, context);
    },
    onError: (error, variables, context) => {
      options?.onError?.(error, variables, context);
    },
  });
};
