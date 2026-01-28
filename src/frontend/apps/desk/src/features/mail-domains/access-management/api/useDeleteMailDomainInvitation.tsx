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

import { KEY_LIST_INVITATION_DOMAIN_ACCESSES } from './useInvitationMailDomainAccesses';

interface DeleteMailDomainInvitationProps {
  slug: string;
  invitationId: string;
}

export const deleteMailDomainInvitation = async ({
  slug,
  invitationId,
}: DeleteMailDomainInvitationProps): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${slug}/invitations/${invitationId}/`,
    {
      method: 'DELETE',
    },
  );

  if (!response.ok) {
    throw new APIError(
      'Failed to delete the invitation',
      await errorCauses(response),
    );
  }
};

type UseDeleteMailDomainInvitationOptions = UseMutationOptions<
  void,
  APIError,
  DeleteMailDomainInvitationProps
>;

export const useDeleteMailDomainInvitation = (
  options?: UseDeleteMailDomainInvitationOptions,
) => {
  const queryClient = useQueryClient();
  const {
    onSuccess: optionsOnSuccess,
    onError: optionsOnError,
    ...restOptions
  } = options || {};
  return useMutation<void, APIError, DeleteMailDomainInvitationProps>({
    mutationFn: deleteMailDomainInvitation,
    ...restOptions,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_INVITATION_DOMAIN_ACCESSES],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_MAIL_DOMAIN],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN],
      });
      if (optionsOnSuccess) {
        (
          optionsOnSuccess as unknown as (
            data: void,
            variables: DeleteMailDomainInvitationProps,
            context: unknown,
          ) => void
        )(data, variables, context);
      }
    },
    onError: (error, variables, context) => {
      if (optionsOnError) {
        (
          optionsOnError as unknown as (
            error: APIError,
            variables: DeleteMailDomainInvitationProps,
            context: unknown,
          ) => void
        )(error, variables, context);
      }
    },
  });
};
