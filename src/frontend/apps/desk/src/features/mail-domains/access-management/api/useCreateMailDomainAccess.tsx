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
  const {
    onSuccess: optionsOnSuccess,
    onError: optionsOnError,
    ...restOptions
  } = options || {};

  return useMutation<Access, APIError, CreateMailDomainAccessProps>({
    mutationFn: createMailDomainAccess,
    ...restOptions,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN_ACCESSES],
      });
      void queryClient.invalidateQueries({ queryKey: [KEY_MAIL_DOMAIN] });
      if (optionsOnSuccess) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          optionsOnSuccess as unknown as (
            data: Access,
            variables: CreateMailDomainAccessProps,
            context: unknown,
          ) => void
        )(data, variables, context);
      }
    },
    onError: (error, variables, context) => {
      if (optionsOnError) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          optionsOnError as unknown as (
            error: APIError,
            variables: CreateMailDomainAccessProps,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
