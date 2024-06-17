import {
  Button,
  DataGrid,
  Loader,
  SortModel,
  usePagination,
} from '@openfun/cunningham-react';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Card, Text, TextErrors } from '@/components';

import { useMailboxes } from '../api/useMailboxes';
import { default as MailDomainsLogo } from '../assets/mail-domains-logo.svg';
import { PAGE_SIZE } from '../conf';
import { MailDomain, MailDomainMailbox } from '../types';

import { CreateMailboxForm } from './forms/CreateMailboxForm';

export type ViewMailbox = { email: string; id: string };

// FIXME : ask Cunningham to export this type
type SortModelItem = {
  field: string;
  sort: 'asc' | 'desc' | null;
};

const defaultOrderingMapping: Record<string, string> = {
  email: 'local_part',
};

/**
 * Formats the sorting model based on a given mapping.
 * @param {SortModelItem} sortModel The sorting model item containing field and sort direction.
 * @param {Record<string, string>} mapping The mapping object to map field names.
 * @returns {string} The formatted sorting string.
 */
function formatSortModel(
  sortModel: SortModelItem,
  mapping = defaultOrderingMapping,
) {
  const { field, sort } = sortModel;
  const orderingField = mapping[field] || field;
  return sort === 'desc' ? `-${orderingField}` : orderingField;
}

export function MailDomainsContent({ mailDomain }: { mailDomain: MailDomain }) {
  const [sortModel, setSortModel] = useState<SortModel>([]);
  const [isCreateMailboxFormVisible, setIsCreateMailboxFormVisible] =
    useState(false);

  const { t } = useTranslation();

  const pagination = usePagination({
    defaultPage: 1,
    pageSize: PAGE_SIZE,
  });

  const { page, pageSize, setPagesCount } = pagination;
  const ordering = sortModel.length ? formatSortModel(sortModel[0]) : undefined;

  const { data, isLoading, error } = useMailboxes({
    mailDomainSlug: mailDomain.slug,
    page,
    ordering,
  });

  const viewMailboxes: ViewMailbox[] =
    mailDomain && data?.results?.length
      ? data.results.map((mailbox: MailDomainMailbox) => ({
          email: `${mailbox.local_part}@${mailDomain.name}`,
          id: mailbox.id,
        }))
      : [];

  useEffect(() => {
    setPagesCount(data?.count ? Math.ceil(data.count / pageSize) : 0);
  }, [data?.count, pageSize, setPagesCount]);
  return isLoading ? (
    <Box $align="center" $justify="center" $height="100%">
      <Loader />
    </Box>
  ) : (
    <>
      {isCreateMailboxFormVisible && mailDomain ? (
        <CreateMailboxForm
          mailDomain={mailDomain}
          setIsFormVisible={setIsCreateMailboxFormVisible}
        />
      ) : null}
      <TopBanner
        name={mailDomain.name}
        setIsFormVisible={setIsCreateMailboxFormVisible}
      />
      <Card
        $padding={{ bottom: 'small' }}
        $margin={{ all: 'big', top: 'none' }}
        $overflow="auto"
      >
        {error && <TextErrors causes={error.cause} />}
        <DataGrid
          columns={[
            {
              field: 'email',
              headerName: t('Emails'),
            },
          ]}
          rows={viewMailboxes}
          isLoading={isLoading}
          onSortModelChange={setSortModel}
          sortModel={sortModel}
          pagination={{
            ...pagination,
            displayGoto: false,
          }}
          aria-label={t('Mailboxes list')}
        />
      </Card>
    </>
  );
}

const TopBanner = ({
  name,
  setIsFormVisible,
}: {
  name: string;
  setIsFormVisible: (value: boolean) => void;
}) => {
  const { t } = useTranslation();

  return (
    <>
      <Box
        $direction="row"
        $align="center"
        $margin={{ all: 'big', vertical: 'xbig' }}
        $gap="2.25rem"
      >
        <MailDomainsLogo aria-label={t('Mail Domains icon')} />
        <Text $margin="none" as="h3" $size="h3">
          {name}
        </Text>
      </Box>
      <Box $margin={{ all: 'big', bottom: 'small' }} $align="flex-end">
        <Button
          aria-label={t(`Create a mailbox in {{name}} domain`, { name })}
          onClick={() => setIsFormVisible(true)}
        >
          {t('Create a mailbox')}
        </Button>
      </Box>
    </>
  );
};
