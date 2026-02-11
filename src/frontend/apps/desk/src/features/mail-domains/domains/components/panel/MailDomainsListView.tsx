import { Button, DataGrid, SortModel } from '@openfun/cunningham-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, StyledLink, Tag, Text } from '@/components';
import { MailDomain, useMailDomains } from '@/features/mail-domains/domains';
import { sortData } from '@/utils/sortData';

interface MailDomainsListViewProps {
  querySearch: string;
}

type ViewMailDomain = {
  id: MailDomain['id'];
  name: string;
  count_mailboxes?: number;
  status: MailDomain['status'];
  slug: string;
  mailDomain: MailDomain;
};

export function MailDomainsListView({ querySearch }: MailDomainsListViewProps) {
  const { t } = useTranslation();

  const [sortModel, setSortModel] = useState<SortModel>([
    {
      field: 'name',
      sort: 'desc',
    },
  ]);

  const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useMailDomains({});

  const mailDomains: ViewMailDomain[] = useMemo(() => {
    if (!data?.pages?.length) {
      return [];
    }
    return data.pages.flatMap((page) =>
      page.results.map((mailDomain: MailDomain) => ({
        id: mailDomain.id,
        name: mailDomain.name,
        count_mailboxes: mailDomain.count_mailboxes,
        status: mailDomain.status,
        slug: mailDomain.slug,
        mailDomain: mailDomain,
      })),
    );
  }, [data]);

  const filteredMailDomains = useMemo(() => {
    let result = mailDomains;

    if (querySearch) {
      const lowerCaseSearch = querySearch.toLowerCase();
      result = result.filter((domain) =>
        domain.name.toLowerCase().includes(lowerCaseSearch),
      );
    }

    return sortData(result, sortModel);
  }, [querySearch, mailDomains, sortModel]);

  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!hasNextPage) {
      return;
    }
    const ref = loadMoreRef.current;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          void fetchNextPage();
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
    <div role="listbox">
      {filteredMailDomains && filteredMailDomains.length ? (
        <DataGrid
          aria-label="listboxDomains"
          rows={filteredMailDomains}
          columns={[
            {
              field: 'name',
              headerName: `${t('Domain')} (${filteredMailDomains.length})`,
            },
            {
              field: 'count_mailboxes',
              headerName: `${t('Number of mailboxes')}`,
            },
            {
              id: 'status',
              field: 'status',
              headerName: `${t('Status')}`,
              renderCell({ row }) {
                return (
                  <Box $direction="row" $align="center">
                    <Tag
                      showTooltip={true}
                      status={row.status}
                      tooltipType="domain"
                    ></Tag>
                  </Box>
                );
              },
            },
            {
              id: 'actions',
              renderCell({ row }) {
                return (
                  <StyledLink
                    aria-label={`${row.name} listboxDomains button`}
                    href={`/mail-domains/${row.slug}`}
                  >
                    <Button
                      style={{
                        fontWeight: '500',
                        fontSize: '16px',
                      }}
                      color="tertiary"
                    >
                      {t('Manage')}
                    </Button>
                  </StyledLink>
                );
              },
            },
          ]}
          isLoading={isLoading}
          sortModel={sortModel}
          onSortModelChange={setSortModel}
        />
      ) : null}
      <div ref={loadMoreRef} style={{ height: 32 }} />
      {isFetchingNextPage && <div>{t('Loading more...')}</div>}
      {!filteredMailDomains ||
        (!filteredMailDomains.length && (
          <Text $align="center" $size="small">
            {t('No domains exist.')}
          </Text>
        ))}
    </div>
  );
}
