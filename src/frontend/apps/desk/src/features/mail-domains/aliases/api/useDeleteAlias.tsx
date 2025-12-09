import {
  UseMutationOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';

import { KEY_LIST_ALIAS } from './useAliases';

interface DeleteAliasParams {
  mailDomainSlug: string;
  localPart: string;
}

// Suppression de l’alias complet (API actuelle)
export const deleteAlias = async ({
  mailDomainSlug,
  localPart,
}: DeleteAliasParams): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/aliases/${localPart}/`,
    {
      method: 'DELETE',
    },
  );

  if (!response.ok) {
    throw new APIError(
      'Failed to delete the alias',
      await errorCauses(response),
    );
  }
};

type UseDeleteAliasOptions = UseMutationOptions<void, APIError, DeleteAliasParams>;

export const useDeleteAlias = (options?: UseDeleteAliasOptions) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, DeleteAliasParams>({
    mutationFn: deleteAlias,
    ...options,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_ALIAS],
      });
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
  });
};

// Suppression d’une destination précise (à activer quand l’API l’exposera)
interface DeleteAliasDestinationParams extends DeleteAliasParams {
  destination: string;
}

export const deleteAliasDestination = async ({
  mailDomainSlug,
  localPart,
  destination,
}: DeleteAliasDestinationParams): Promise<void> => {
  const response = await fetchAPI(
    `mail-domains/${mailDomainSlug}/aliases/${localPart}/${destination}/`,
    {
      method: 'DELETE',
    },
  );

  if (!response.ok) {
    throw new APIError(
      'Failed to delete the alias destination',
      await errorCauses(response),
    );
  }
};

type UseDeleteAliasDestinationOptions = UseMutationOptions<
  void,
  APIError,
  DeleteAliasDestinationParams
>;

export const useDeleteAliasDestination = (
  options?: UseDeleteAliasDestinationOptions,
) => {
  const queryClient = useQueryClient();
  return useMutation<void, APIError, DeleteAliasDestinationParams>({
    mutationFn: deleteAliasDestination,
    ...options,
    onSuccess: (data, variables, context) => {
      void queryClient.invalidateQueries({
        queryKey: [KEY_LIST_ALIAS],
      });
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
  });
};

