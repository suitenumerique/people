import { PropsWithChildren, useMemo, useRef } from 'react';
import { useConfigStore } from '@/core';

import { Box, Card, Text, Tag, StyledLink } from '@/components';
import { MainLayout } from '@/layouts';
import { MailDomainsTopBar } from '@/features/mail-domains/domains';

import { useCunninghamTheme } from '@/cunningham';
import { DataGrid, Button } from "@openfun/cunningham-react";

import {
  MailDomain,
  useMailDomains,
  useMailDomainsStore,
} from '@/features/mail-domains/domains';

import { Panel } from './panel';

interface PanelMailDomainsStateProps {
  isLoading: boolean;
  isError: boolean;
  mailDomains?: MailDomain[];
}

export function MailDomainsListView({ children }: PropsWithChildren) {
  const { colorsTokens } = useCunninghamTheme();
  const { ordering } = useMailDomainsStore();
  const {
    data,
    isError,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useMailDomains({ ordering });
  const containerRef = useRef<HTMLDivElement>(null);
  const mailDomains = useMemo(() => {
    return data?.pages.reduce((acc, page) => {
      return acc.concat(page.results);
    }, [] as MailDomain[]);
  }, [data?.pages]);

  return (
    <div>
        {mailDomains && mailDomains.length ? (
          <DataGrid rows={mailDomains} 
            columns={[{
              field: "name",
              headerName: "Domaine",
            }, {
              field: "id",
              headerName: "Nombre d'adresses",
              enableSorting: true,
            },
            {
              id: "status",
              headerName: "Statut",
              enableSorting: true,
              renderCell({ row }) {
                const tooltipText = {
                  'pending': "Domaine en cours de validation par un administrateur",
                  'enabled': "Domaine actif",
                  'disabled': "Domaine désactivé",
                  'failed': "Domaine en erreur, contactez un administrateur",
                }

                return (
                  <Box $direction="row" $align="center">
                    <Tag status={row.status} tooltip={tooltipText[row.status] || null }></Tag>
                  </Box>
                )
              }
            },
            {
              id: "actions",
              renderCell({ row }) {
                return (
                  <StyledLink 
                    href={`/mail-domains/${row.slug}`}>
                    <Button 
                      style={{
                        fontWeight: '500',
                        fontSize: '16px'
                      }}
                      color="tertiary">
                        Gérer
                      </Button>
                  </StyledLink>
                );
              }
            }
            ]
          } />) : null
        }
      </div>
  );
}
