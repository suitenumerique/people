import { useMutation } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { User } from '@/core/auth';
import { Invitation, OptionType } from '@/features/teams/member-add/types';

import { MailDomain, Role } from '../../domains';

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
  return useMutation<Invitation, APIError, CreateInvitationParams>({
    mutationFn: createInvitation,
  });
}
