import { DataGrid, SortModel } from '@openfun/cunningham-react';
import type { InfiniteData } from '@tanstack/react-query';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text, TextErrors } from '@/components';
import { MailDomain } from '@/features/mail-domains/domains';
import { Alias, ViewAlias } from '@/features/mail-domains/aliases/types';

import { useAliasesInfinite } from '../../api/useAliasesInfinite';

import { PanelActions } from './PanelActions';

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

type SortModelItem = {
  field: string;
  sort: 'asc' | 'desc' | null;
};

function formatSortModel(sortModel: SortModelItem) {
  return sortModel.sort === 'desc' ? `-${sortModel.field}` : sortModel.field;
}

export function AliasesListView({
  mailDomain,
  querySearch,
}: AliasesListViewProps) {
  const { t } = useTranslation();

  const [sortModel] = useState<SortModel>([]);

  const ordering = sortModel.length ? formatSortModel(sortModel[0]) : undefined;
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useAliasesInfinite({
    mailDomainSlug: mailDomain.slug,
    ordering,
  }) as {
    data: InfiniteData<MailDomainAliasesResponse, number> | undefined;
    isLoading: boolean;
    error: { cause?: string[] };
    fetchNextPage: () => void;
    hasNextPage: boolean | undefined;
    isFetchingNextPage: boolean;
  };

  const aliases: ViewAlias[] = useMemo(() => {
    if (!mailDomain || !data?.pages?.length) {
      return [];
    }
    return data.pages.flatMap((page) =>
      page.results.map((alias: Alias) => {
        const email = `${alias.local_part}@${mailDomain.name}`;

        return {
          id: alias.id,
          email,
          local_part: alias.local_part,
          destination: alias.destination,
          alias,
        };
      }),
    );
  }, [data, mailDomain]);

  const filteredAliases = useMemo(() => {
    if (!querySearch) {
      return aliases;
    }
    const lowerCaseSearch = querySearch.toLowerCase();
    return aliases.filter(
      (alias) =>
        alias.email.toLowerCase().includes(lowerCaseSearch) ||
        alias.destination.toLowerCase().includes(lowerCaseSearch),
    );
  }, [querySearch, aliases]);

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

      {filteredAliases && filteredAliases.length ? (
        <>
          <DataGrid
            aria-label="aliaslist"
            rows={filteredAliases}
            columns={[
              {
                field: 'email',
                headerName: `${t('Alias')} • ${filteredAliases.length}`,
                renderCell: ({ row }) => (
                  <Text $weight="400" $theme="greyscale">
                    {row.email}
                  </Text>
                ),
              },
              {
                field: 'destination',
                headerName: t('Destination'),
                enableSorting: true,
                renderCell: ({ row }) => (
                  <Text $weight="500" $theme="greyscale">
                    {row.destination}
                  </Text>
                ),
              },
              {
                id: 'actions',
                renderCell: ({ row }) => (
                  <PanelActions mailDomain={mailDomain} alias={row} />
                ),
              },
            ]}
            isLoading={isLoading}
          />
          {isFetchingNextPage && <div>{t('Loading more...')}</div>}
        </>
      ) : null}
      <div ref={loadMoreRef} style={{ height: 32 }} />
    </div>
  );
}


