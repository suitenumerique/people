import { useMutation } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { User } from '@/core/auth';
import { Role, MailDomain } from '../../domains';

import { Invitation, OptionType } from '../types';

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
  const response = await fetchAPI(`mail-domains/${mailDomainSlug}/invitations/`, {
    method: 'POST',
    body: JSON.stringify({
      email,
      role,
    }),
  });

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
