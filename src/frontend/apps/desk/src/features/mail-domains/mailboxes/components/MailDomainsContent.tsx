import { UUID } from 'crypto';

import {
  Alert,
  Button,
  DataGrid,
  Loader,
  SortModel,
  VariantType,
  usePagination,
} from '@openfun/cunningham-react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Card, Text, TextErrors, TextStyled } from '@/components';
import { ModalCreateMailbox } from '@/features/mail-domains/mailboxes';

import { PAGE_SIZE } from '../../conf';
import { MailDomain } from '../../domains/types';
import { useMailboxes } from '../api/useMailboxes';
import { MailDomainMailbox } from '../types';

import { MailDomainsActions } from './MailDomainsActions';

export type ViewMailbox = {
  name: string;
  email: string;
  id: UUID;
  status: MailDomainMailbox['status'];
  mailbox: MailDomainMailbox;
};

// FIXME : ask Cunningham to export this type
type SortModelItem = {
  field: string;
  sort: 'asc' | 'desc' | null;
};

const defaultOrderingMapping: Record<string, string> = {
  email: 'local_part',
};

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
          name: `${mailbox.first_name} ${mailbox.last_name}`,
          id: mailbox.id,
          status: mailbox.status,
          mailbox,
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
        <ModalCreateMailbox
          mailDomain={mailDomain}
          closeModal={() => setIsCreateMailboxFormVisible(false)}
        />
      ) : null}

      <TopBanner
        mailDomain={mailDomain}
        showMailBoxCreationForm={setIsCreateMailboxFormVisible}
      />

      <Card
        $overflow="auto"
        aria-label={t('Mailboxes list card')}
        $css={`
          
          & table td:last-child {
            text-align: right;
          }
      `}
      >
        {error && <TextErrors causes={error.cause} />}

        <DataGrid
          columns={[
            {
              field: 'name',
              headerName: t('Names'),
              renderCell: ({ row }) => (
                <Text
                  $weight="bold"
                  $theme="primary"
                  $css="text-transform: capitalize;"
                >
                  {row.name}
                </Text>
              ),
            },
            {
              field: 'email',
              headerName: t('Emails'),
            },
            {
              field: 'status',
              headerName: t('Status'),
            },
            {
              id: 'column-actions',
              renderCell: ({ row }) => (
                <MailDomainsActions
                  mailbox={row.mailbox}
                  mailDomain={mailDomain}
                />
              ),
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
          hideEmptyPlaceholderImage={true}
          emptyPlaceholderLabel={t(
            'No mail box was created with this mail domain.',
          )}
        />
      </Card>
    </>
  );
}

const TopBanner = ({
  mailDomain,
  showMailBoxCreationForm,
}: {
  mailDomain: MailDomain;
  showMailBoxCreationForm: (value: boolean) => void;
}) => {
  const { t } = useTranslation();
  const canCreateMailbox =
    mailDomain.status === 'enabled' || mailDomain.status === 'pending';

  return (
    <Box $direction="column" $gap="1rem">
      <AlertStatus status={mailDomain.status} />

      <Box
        $direction="row"
        $justify="flex-end"
        $margin={{ bottom: 'small' }}
        $align="center"
      >
        <Box $display="flex" $direction="row">
          {mailDomain?.abilities.post && (
            <Button
              aria-label={t('Create a mailbox in {{name}} domain', {
                name: mailDomain?.name,
              })}
              disabled={!canCreateMailbox}
              onClick={() => showMailBoxCreationForm(true)}
            >
              {t('Create a mailbox')}
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

const AlertStatus = ({ status }: { status: MailDomain['status'] }) => {
  const { t } = useTranslation();

  const getStatusAlertProps = (status?: string) => {
    switch (status) {
      case 'disabled':
        return {
          variant: VariantType.NEUTRAL,
          message: t(
            'This domain name is deactivated. No new mailboxes can be created.',
          ),
        };
      case 'failed':
        return {
          variant: VariantType.ERROR,
          message: (
            <Text $display="inline">
              {t(
                'The domain name encounters an error. Please contact our support team to solve the problem:',
              )}{' '}
              <TextStyled
                as="a"
                target="_blank"
                $display="inline"
                href="mailto:suiteterritoriale@anct.gouv.fr"
                aria-label={t(
                  'Contact our support at "suiteterritoriale@anct.gouv.fr"',
                )}
              >
                suiteterritoriale@anct.gouv.fr
              </TextStyled>
              .
            </Text>
          ),
        };
    }
  };

  const alertStatusProps = getStatusAlertProps(status);

  if (!alertStatusProps) {
    return null;
  }

  return (
    <Alert canClose={false} type={alertStatusProps.variant}>
      <Text $display="inline">{alertStatusProps.message}</Text>
    </Alert>
  );
};
