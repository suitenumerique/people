import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import {
  KEY_LIST_MAIL_DOMAIN,
  KEY_MAIL_DOMAIN,
} from '@/features/mail-domains/domains';

import { KEY_LIST_MAIL_DOMAIN_ACCESSES } from './useMailDomainAccesses';

interface DeleteMailDomainAccessProps {
  slug: string;
  accessId: string;
}

export const deleteMailDomainAccess = async ({
  slug,
  accessId,
}: DeleteMailDomainAccessProps): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${slug}/accesses/${accessId}/`,
    {
      method: 'DELETE',
    },
  );

  if (!response.ok) {
    throw new APIError(
      'Failed to delete the access',
      await errorCauses(response),
    );
  }
};

type UseDeleteMailDomainAccessOptions = UseMutationOptions<
  void,
  APIError,
  DeleteMailDomainAccessProps
>;

export const useDeleteMailDomainAccess = (
  options?: UseDeleteMailDomainAccessOptions,
) => {
  const queryClient = useQueryClient();
  const {
    onSuccess: optionsOnSuccess,
    onError: optionsOnError,
    ...restOptions
  } = options || {};
  return useMutation<void, APIError, DeleteMailDomainAccessProps>({
    mutationFn: deleteMailDomainAccess,
    ...restOptions,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN_ACCESSES],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_MAIL_DOMAIN],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN],
      });
      if (optionsOnSuccess) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-explicit-any
        (
          optionsOnSuccess as unknown as (
            data: void,
            variables: DeleteMailDomainAccessProps,
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
            variables: DeleteMailDomainAccessProps,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
