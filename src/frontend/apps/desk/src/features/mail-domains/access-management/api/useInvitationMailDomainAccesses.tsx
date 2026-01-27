import { UseQueryOptions, useQuery } from '@tanstack/react-query';

import { APIError, APIList, errorCauses, fetchAPI } from '@/api';

import { Access } from '../types';

export type InvitationMailDomainAccessesAPIParams = {
  slug: string;
};

type AccessesResponse = APIList<Access>;

export const getInvitationMailDomainAccesses = async ({
  slug,
}: InvitationMailDomainAccessesAPIParams): Promise<AccessesResponse> => {
  const url = `mail-domains/${slug}/invitations/`;

  const response = await fetchAPI(url);

  if (!response.ok) {
    throw new APIError(
      'Failed to get the invitations',
      await errorCauses(response),
    );
  }

  return response.json() as Promise<AccessesResponse>;
};

export const KEY_LIST_INVITATION_DOMAIN_ACCESSES =
  'invitation-mail-domains-accesses';

export function useInvitationMailDomainAccesses(
  params: InvitationMailDomainAccessesAPIParams,
  queryConfig?: UseQueryOptions<AccessesResponse, APIError, AccessesResponse>,
) {
  return useQuery<AccessesResponse, APIError, AccessesResponse>({
    queryKey: [KEY_LIST_INVITATION_DOMAIN_ACCESSES, params],
    queryFn: () => getInvitationMailDomainAccesses(params),
    ...queryConfig,
  });
}
