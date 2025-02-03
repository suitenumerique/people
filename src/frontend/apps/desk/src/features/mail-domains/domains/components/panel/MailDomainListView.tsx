import { Button, SimpleDataGrid } from '@openfun/cunningham-react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, StyledLink, Tag } from '@/components';
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
  const { data, isLoading } = useMailDomains({ ordering });
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

  return (
    <div>
      {filteredMailDomains && filteredMailDomains.length ? (
        <SimpleDataGrid
          aria-label="listbox"
          rows={filteredMailDomains}
          columns={[
            {
              field: 'name',
              headerName: 'Domaine',
              enableSorting: true,
            },
            {
              field: 'count_mailboxes',
              headerName: "Nombre d'adresses",
              enableSorting: true,
            },
            {
              id: 'status',
              headerName: 'Statut',
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
                    href={`/mail-domains/${row.slug}`}
                    aria-label="`${row.name} listbox button`"
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
        />
      ) : null}
    </div>
  );
}
