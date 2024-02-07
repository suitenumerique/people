import {
  DefinedInitialDataInfiniteOptions,
  InfiniteData,
  QueryKey,
  useInfiniteQuery,
} from '@tanstack/react-query';

import { APIList, fetchAPI } from '@/api';

import { TeamResponse } from './types';

export enum TeamsOrdering {
  BY_CREATED_ON = 'created_at',
  BY_CREATED_ON_DESC = '-created_at',
}

export type TeamsParams = {
  ordering: TeamsOrdering;
};
type TeamsAPIParams = TeamsParams & {
  page: number;
};

type TeamsResponse = APIList<TeamResponse>;
export interface TeamsResponseError {
  detail: string;
}

export const getTeams = async ({
  ordering,
  page,
}: TeamsAPIParams): Promise<TeamsResponse> => {
  const orderingQuery = ordering ? `&ordering=${ordering}` : '';
  const response = await fetchAPI(`teams/?page=${page}${orderingQuery}`);

  if (!response.ok) {
    throw new Error(`Couldn't fetch teams: ${response.statusText}`);
  }
  return response.json() as Promise<TeamsResponse>;
};

export const KEY_LIST_TEAM = 'teams';

export function useTeams(
  param: TeamsParams,
  queryConfig?: DefinedInitialDataInfiniteOptions<
    TeamsResponse,
    TeamsResponseError,
    InfiniteData<TeamsResponse>,
    QueryKey,
    number
  >,
) {
  return useInfiniteQuery<
    TeamsResponse,
    TeamsResponseError,
    InfiniteData<TeamsResponse>,
    QueryKey,
    number
  >({
    initialPageParam: 1,
    queryKey: [KEY_LIST_TEAM, param],
    queryFn: ({ pageParam }) =>
      getTeams({
        ...param,
        page: pageParam,
      }),
    getNextPageParam(lastPage, allPages) {
      return lastPage.next ? allPages.length + 1 : undefined;
    },
    ...queryConfig,
  });
}
