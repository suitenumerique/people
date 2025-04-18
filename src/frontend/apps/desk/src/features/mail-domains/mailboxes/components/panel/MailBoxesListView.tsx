import { Button, DataGrid, SortModel, usePagination } from '@openfun/cunningham-react';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMailboxes } from '../../api/useMailboxes';
import { PAGE_SIZE } from '../../../conf';

import { Box, StyledLink, Tag, Text, TextErrors } from '@/components';
import {
  MailDomain,
} from '@/features/mail-domains/domains';

import { PanelActions } from './PanelActions';

interface MailBoxesListViewProps {
  mailDomain: MailDomain,
  querySearch: string;
}

type SortModelItem = {
  field: string;
  sort: 'asc' | 'desc' | null;
};

function formatSortModel(
  sortModel: SortModelItem,
  mapping = defaultOrderingMapping,
) {
  const { field, sort } = sortModel;
  const orderingField = mapping[field] || field;
  return sort === 'desc' ? `-${orderingField}` : orderingField;
}

export type ViewMailbox = {
  name: string;
  email: string;
  id: UUID;
  status: MailDomainMailbox['status'];
  mailbox: MailDomainMailbox;
};


export function MailBoxesListView({ mailDomain, querySearch }: MailBoxesListViewProps) {
  const { t } = useTranslation();

  const [sortModel, setSortModel] = useState<SortModel>([]);
  
  const pagination = usePagination({
    defaultPage: 1,
    pageSize: PAGE_SIZE,
  });

  const { page, pageSize, setPagesCount } = pagination;

  const defaultOrderingMapping: Record<string, string> = {
    email: 'local_part',
  };
  const ordering = sortModel.length ? formatSortModel(sortModel[0]) : undefined;
  const { data, isLoading, error } = useMailboxes({
    mailDomainSlug: mailDomain.slug,
    page,
    ordering,
  });

  const mailDomains = useMemo(() => {
    if (!data?.pages) return [];
    return data.pages.reduce((acc, page) => {
      return acc.concat(page.results);
    }, [] as MailDomain[]);
  }, [data?.pages]);


  const mailboxes: ViewMailbox[] =
    mailDomain && data?.results?.length
      ? data.results.map((mailbox: MailDomainMailbox) => ({
          email: `${mailbox.local_part}@${mailDomain.name}`,
          name: `${mailbox.first_name} ${mailbox.last_name}`,
          id: mailbox.id,
          status: mailbox.status,
          mailbox,
        }))
    : [];

  const filteredMailboxes = useMemo(() => {
    if (!querySearch) {
      return mailboxes;
    }
    const lowerCaseSearch = querySearch.toLowerCase();
    return (
      (mailboxes &&
        mailboxes.filter((mailbox) =>
          mailbox.email.toLowerCase().includes(lowerCaseSearch),
        )) ||
      []
    );
  }, [querySearch, mailboxes]);

  return (
    <div>
      {error && <TextErrors causes={error.cause} />}

      {filteredMailboxes && filteredMailboxes.length ? (
        <DataGrid
          aria-label="listbox"
          rows={filteredMailboxes}
          columns={[
            {
              field: 'email',
              headerName: `${t('Address')} • ${filteredMailboxes.length}`,
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
                      showTooltip="true"
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
                <>
                <PanelActions
                  mailbox={row.mailbox}
                  mailDomain={mailDomain}
                />
                </>
              )
            },
          ]}
          isLoading={isLoading}
        />
      ) : null}
    </div>
  );
}
