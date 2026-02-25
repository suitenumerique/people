import { Button, DataGrid } from '@gouvfr-lasuite/cunningham-react';
import { useEffect, useMemo, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { MailDomainLogoCircle } from '../MailDomainLogoCircle';
import { Box, StyledLink, Tag, Text } from '@/components';
import {
  MailDomain,
  useMailDomains,
  useMailDomainsStore,
} from '@/features/mail-domains/domains';

interface MailDomainsListViewProps {
  querySearch: string;
}

export function MailDomainsListView({ querySearch }: MailDomainsListViewProps) {
  const { t } = useTranslation();

  const { ordering } = useMailDomainsStore();
  const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useMailDomains({ ordering });
  const mailDomains = useMemo(() => {
    return data?.pages.reduce((acc, page) => {
      return acc.concat(page.results);
    }, [] as MailDomain[]);
  }, [data?.pages]);

  const filteredMailDomains = useMemo(() => {
    if (!querySearch) {
      return mailDomains;
    }
    const lowerCaseSearch = querySearch.toLowerCase();
    return (
      (mailDomains &&
        mailDomains.filter((domain) =>
          domain.name.toLowerCase().includes(lowerCaseSearch),
        )) ||
      []
    );
  }, [querySearch, mailDomains]);

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
              enableSorting: true,
              renderCell({ row }) {
                return (
                  <Box $direction="row" $gap="8px" $align="center">
                    <MailDomainLogoCircle size={24} />
                    <Text>{row.name}</Text>
                  </Box>
                );
              },
            },
            {
              field: 'count_mailboxes',
              headerName: `${t('Number of mailboxes')}`,
              enableSorting: true,
            },
            {
              id: 'status',
              headerName: `${t('Status')}`,
              enableSorting: true,
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
                      size="small"
                      theme="brand"
                      variant="secondary"
                      iconPosition="right"
                      icon={<span className="material-icons">arrow_forward</span>}
                    >
                      {t('Manage')}
                    </Button>
                  </StyledLink>
                );
              },
            },
          ]}
          isLoading={isLoading}
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
