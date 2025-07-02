import { DataGrid, SortModel } from '@openfun/cunningham-react';
import type { InfiniteData } from '@tanstack/react-query';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Tag, Text, TextErrors } from '@/components';
import { MailDomain } from '@/features/mail-domains/domains';
import {
  MailDomainMailbox,
  MailDomainMailboxStatus,
} from '@/features/mail-domains/mailboxes/types';

import { useMailboxesInfinite } from '../../api/useMailboxesInfinite';

import { PanelActions } from './PanelActions';

type MailDomainMailboxesResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: MailDomainMailbox[];
};

interface MailBoxesListViewProps {
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

export type ViewMailbox = {
  name: string;
  id: string;
  email: string;
  status: MailDomainMailboxStatus;
};

export function MailBoxesListView({
  mailDomain,
  querySearch,
}: MailBoxesListViewProps) {
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
  } = useMailboxesInfinite({
    mailDomainSlug: mailDomain.slug,
    ordering,
  }) as {
    data: InfiniteData<MailDomainMailboxesResponse, number> | undefined;
    isLoading: boolean;
    error: { cause?: string[] };
    fetchNextPage: () => void;
    hasNextPage: boolean | undefined;
    isFetchingNextPage: boolean;
  };

  const mailboxes: ViewMailbox[] = useMemo(() => {
    if (!mailDomain || !data?.pages?.length) {
      return [];
    }
    return data.pages.flatMap((page) =>
      page.results.map((mailbox: MailDomainMailbox) => ({
        email: `${mailbox.local_part}@${mailDomain.name}`,
        name: `${mailbox.first_name} ${mailbox.last_name}`,
        id: mailbox.id,
        status: mailbox.status,
        mailbox,
      })),
    );
  }, [data, mailDomain]);

  const filteredMailboxes = useMemo(() => {
    if (!querySearch) {
      return mailboxes;
    }
    const lowerCaseSearch = querySearch.toLowerCase();
    return mailboxes.filter((mailbox) =>
      mailbox.email.toLowerCase().includes(lowerCaseSearch),
    );
  }, [querySearch, mailboxes]);

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

      {filteredMailboxes && filteredMailboxes.length ? (
        <>
          <DataGrid
            aria-label="listbox"
            rows={filteredMailboxes}
            columns={[
              {
                field: 'email',
                headerName: `${t('Address')} • ${filteredMailboxes.length}`,
                renderCell: ({ row }) => <Text>{row.email}</Text>,
              },
              {
                field: 'name',
                headerName: t('User'),
                enableSorting: true,
                renderCell: ({ row }) => (
                  <Text
                    $weight="500"
                    $theme="greyscale"
                    $css="text-transform: capitalize;"
                  >
                    {row.name}
                  </Text>
                ),
              },
              {
                id: 'status',
                headerName: t('Status'),
                enableSorting: true,
                renderCell({ row }) {
                  return (
                    <Box $direction="row" $align="center">
                      <Tag
                        showTooltip={true}
                        status={row.status}
                        tooltipType="mail"
                      ></Tag>
                    </Box>
                  );
                },
              },
              {
                id: 'actions',
                renderCell: ({ row }) => (
                  <PanelActions mailDomain={mailDomain} mailbox={row} />
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
