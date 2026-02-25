import { Button, DataGrid, SortModel } from '@openfun/cunningham-react';
import type { InfiniteData } from '@tanstack/react-query';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text, TextErrors } from '@/components';
import { useAuthStore } from '@/core/auth';
import { Alias, AliasGroup } from '@/features/mail-domains/aliases/types';
import { MailDomain } from '@/features/mail-domains/domains';
import { sortData } from '@/utils/sortData';

import { useAliasesInfinite } from '../../api/useAliasesInfinite';
import { ModalEditAlias } from '../ModalEditAlias';

type MailDomainAliasesResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Alias[];
};

interface AliasesListViewProps {
  mailDomain: MailDomain;
  querySearch: string;
}

export function AliasesListView({
  mailDomain,
  querySearch,
}: AliasesListViewProps) {
  const { t } = useTranslation();
  const { userData } = useAuthStore();
  const [editingAliasGroup, setEditingAliasGroup] = useState<AliasGroup | null>(
    null,
  );

  const [sortModel, setSortModel] = useState<SortModel>([
    {
      field: 'local_part',
      sort: 'desc',
    },
  ]);

  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useAliasesInfinite({
    mailDomainSlug: mailDomain.slug,
  }) as {
    data: InfiniteData<MailDomainAliasesResponse, number> | undefined;
    isLoading: boolean;
    error: { cause?: string[] };
    fetchNextPage: () => void;
    hasNextPage: boolean | undefined;
    isFetchingNextPage: boolean;
  };

  const aliasGroups: AliasGroup[] = useMemo(() => {
    if (!mailDomain || !data?.pages?.length) {
      return [];
    }

    const grouped = new Map<string, AliasGroup>();

    data.pages.forEach((page) => {
      page.results.forEach((alias: Alias) => {
        const email = `${alias.local_part}@${mailDomain.name}`;
        const existing = grouped.get(alias.local_part);
        if (existing) {
          if (!existing.destinations.includes(alias.destination)) {
            existing.destinations.push(alias.destination);
            existing.destinationIds[alias.destination] = alias.id;
            existing.count_destinations = existing.destinations.length;
          }
        } else {
          const destinationIds: Record<string, string> = {};
          destinationIds[alias.destination] = alias.id;
          grouped.set(alias.local_part, {
            id: alias.local_part,
            email,
            local_part: alias.local_part,
            destinations: [alias.destination],
            destinationIds,
            count_destinations: [alias.destination].length,
          });
        }
      });
    });

    return Array.from(grouped.values());
  }, [data, mailDomain]);

  const filteredAliases = useMemo(() => {
    let result = aliasGroups;

    if (querySearch) {
      const lowerCaseSearch = querySearch.toLowerCase();
      result = result.filter(
        (alias) =>
          alias.email.toLowerCase().includes(lowerCaseSearch) ||
          alias.destinations.some((dest) =>
            dest.toLowerCase().includes(lowerCaseSearch),
          ),
      );
    }

    return sortData(result, sortModel);
  }, [querySearch, aliasGroups, sortModel]);

  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!hasNextPage) {
      return;
    }
    const ref = loadMoreRef.current;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 1 },
    );
    if (ref) {
      observer.observe(ref);
    }
    return () => {
      if (ref) {
        observer.unobserve(ref);
      }
    };
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <div>
      {error && <TextErrors causes={error.cause ?? []} />}

      {!filteredAliases.length && (
        <Text $align="center" $size="small" $padding={{ top: 'base' }}>
          {t('No alias was created with this mail domain.')}
        </Text>
      )}

      {filteredAliases && filteredAliases.length ? (
        <>
          <DataGrid
            aria-label="aliaslist"
            rows={filteredAliases}
            columns={[
              {
                field: 'local_part',
                headerName: `${t('Alias')} • ${filteredAliases.length}`,
                renderCell: ({ row }) => (
                  <Text $weight="400" $theme="greyscale">
                    {row.email}
                  </Text>
                ),
              },
              {
                field: 'count_destinations',
                headerName: t('Destinations'),
                renderCell: ({ row }) => (
                  <Text $weight="500" $theme="greyscale">
                    {row.count_destinations} destination
                    {row.count_destinations > 1 ? 's' : ''}
                  </Text>
                ),
              },
              {
                id: 'actions',
                renderCell: ({ row }) => {
                  // Check if user can edit
                  const isOwnerOrAdmin =
                    mailDomain.abilities?.patch || mailDomain.abilities?.put;
                  const isAliasDestination = row.destinations.some(
                    (dest) => dest === userData?.email,
                  );
                  const canEdit = isOwnerOrAdmin || isAliasDestination;

                  return (
                    <Box $direction="row" $gap="sm" $align="center">
                      {canEdit && (
                        <Button
                          color="tertiary"
                          onClick={() => setEditingAliasGroup(row)}
                          style={{
                            fontWeight: '500',
                            fontSize: '16px',
                          }}
                        >
                          {t('Manage')}
                        </Button>
                      )}
                    </Box>
                  );
                },
              },
            ]}
            isLoading={isLoading}
            sortModel={sortModel}
            onSortModelChange={setSortModel}
          />
          {isFetchingNextPage && <div>{t('Loading more...')}</div>}
        </>
      ) : null}
      <div ref={loadMoreRef} />
      {editingAliasGroup && (
        <ModalEditAlias
          mailDomain={mailDomain}
          aliasGroup={editingAliasGroup}
          closeModal={() => setEditingAliasGroup(null)}
        />
      )}
    </div>
  );
}
