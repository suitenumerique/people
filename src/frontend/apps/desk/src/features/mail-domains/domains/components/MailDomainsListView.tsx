import { Button, DataGrid } from '@openfun/cunningham-react';
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
        <DataGrid
          aria-label="listbox"
          rows={filteredMailDomains}
          columns={[
            {
              field: 'name',
              headerName: 'Domaine',
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
                const tooltipText = {
                  pending:
                    'Domaine en cours de validation par un administrateur',
                  enabled: 'Domaine actif',
                  disabled: 'Domaine désactivé',
                  failed: 'Domaine en erreur, contactez un administrateur',
                  action_required:
                    'Une action de paramétrage du gestionnaire du domaine (hors Régie) est requise',
                };

                return (
                  <Box $direction="row" $align="center">
                    <Tag
                      status={row.status}
                      tooltip={tooltipText[row.status] || ''}
                    ></Tag>
                  </Box>
                );
              },
            },
            {
              id: 'actions',
              renderCell({ row }) {
                return (
                  <StyledLink href={`/mail-domains/${row.slug}`}>
                    <Button
                      aria-label="`${row.name} listbox button`"
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
