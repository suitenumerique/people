import { DataGrid, SortModel, usePagination } from '@openfun/cunningham-react';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Tag, Text, TextErrors } from '@/components';
import { MailDomain } from '@/features/mail-domains/domains';
import {
  MailDomainMailbox,
  ViewMailbox,
} from '@/features/mail-domains/mailboxes/types';

import { PAGE_SIZE } from '../../../conf';
import { useMailboxes } from '../../api/useMailboxes';

import { PanelActions } from './PanelActions';

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

export function MailBoxesListView({
  mailDomain,
  querySearch,
}: MailBoxesListViewProps) {
  const { t } = useTranslation();

  const [sortModel] = useState<SortModel>([]);

  const pagination = usePagination({
    defaultPage: 1,
    pageSize: PAGE_SIZE,
  });

  const { page } = pagination;

  const ordering = sortModel.length ? formatSortModel(sortModel[0]) : undefined;
  const { data, isLoading, error } = useMailboxes({
    mailDomainSlug: mailDomain.slug,
    page,
    ordering,
  });

  const mailboxes: ViewMailbox[] = useMemo(() => {
    if (!mailDomain || !data?.results?.length) {
      return [];
    }

    return data.results.map((mailbox: MailDomainMailbox) => ({
      id: mailbox.id,
      first_name: mailbox.first_name,
      last_name: mailbox.last_name,
      local_part: mailbox.local_part,
      secondary_email: mailbox.secondary_email,
      status: mailbox.status,
    }));
  }, [data?.results, mailDomain]);

  const filteredMailboxes = useMemo(() => {
    if (!querySearch) {
      return mailboxes;
    }
    const lowerCaseSearch = querySearch.toLowerCase();
    return (
      (mailboxes &&
        mailboxes.filter((mailbox) =>
          mailbox.local_part.toLowerCase().includes(lowerCaseSearch),
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
              field: 'local_part',
              headerName: `${t('Address')} • ${filteredMailboxes.length}`,
              renderCell: ({ row }) => (
                <Text>
                  {row.local_part}@{mailDomain.name}
                </Text>
              ),
            },
            {
              field: 'first_name',
              headerName: t('User'),
              enableSorting: true,
              renderCell: ({ row }) => (
                <Text
                  $weight="500"
                  $theme="greyscale"
                  $css="text-transform: capitalize;"
                >
                  {row.first_name} {row.last_name}
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
      ) : null}
    </div>
  );
}
