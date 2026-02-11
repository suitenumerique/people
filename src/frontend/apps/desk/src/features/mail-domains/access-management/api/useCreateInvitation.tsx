import { useMutation, useQueryClient } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { User } from '@/core/auth';
import {
  KEY_LIST_MAIL_DOMAIN,
  KEY_MAIL_DOMAIN,
  MailDomain,
  Role,
} from '@/features/mail-domains/domains';
import { Invitation, OptionType } from '@/features/teams/member-add/types';

import { KEY_LIST_INVITATION_DOMAIN_ACCESSES } from './useInvitationMailDomainAccesses';

interface CreateInvitationParams {
  email: User['email'];
  role: Role;
  mailDomainSlug: MailDomain['slug'];
}

export const createInvitation = async ({
  email,
  role,
  mailDomainSlug,
}: CreateInvitationParams): Promise<Invitation> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/invitations/`,
    {
      method: 'POST',
      body: JSON.stringify({
        email,
        role,
      }),
    },
  );

  if (!response.ok) {
    throw new APIError(
      `Failed to create the invitation for ${email}`,
      await errorCauses(response, {
        value: email,
        type: OptionType.INVITATION,
      }),
    );
  }

  return response.json() as Promise<Invitation>;
};

export function useCreateInvitation() {
  const queryClient = useQueryClient();

  return useMutation<Invitation, APIError, CreateInvitationParams>({
    mutationFn: createInvitation,
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_INVITATION_DOMAIN_ACCESSES],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_MAIL_DOMAIN],
      });
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_MAIL_DOMAIN],
      });
    },
  });
}
