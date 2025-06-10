import {
  Alert,
  Button,
  Input,
  Tooltip,
  VariantType,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { ModalCreateMailbox } from '@/features/mail-domains/mailboxes/components';
import { MailBoxesListView } from '@/features/mail-domains/mailboxes/components/panel';

import { MailDomain } from '../../domains/types';

export function MailBoxesView({ mailDomain }: { mailDomain: MailDomain }) {
  const [searchValue, setSearchValue] = useState('');

  const [isCreateMailboxFormVisible, setIsCreateMailboxFormVisible] =
    useState(false);

  const { t } = useTranslation();

  const { colorsTokens } = useCunninghamTheme();
  const colors = colorsTokens();

  const canCreateMailbox =
    mailDomain.status === 'enabled' || mailDomain.status === 'pending';

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const clearInput = () => {
    setSearchValue('');
  };

  const openModal = () => {
    setIsCreateMailboxFormVisible(true);
  };

  return (
    <>
      <div aria-label="Mail Domains panel" className="container">
        <h3 style={{ fontWeight: 700, fontSize: '18px', marginBottom: 'base' }}>
          {t('Email addresses')}
        </h3>
        <div
          style={{
            marginBottom: '20px',
          }}
        >
          <AlertStatus status={mailDomain.status} />
        </div>
        <div
          className="sm:block md:flex"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            gap: '1em',
          }}
        >
          <div
            style={{ width: 'calc(100% - 245px)' }}
            className="c__input__wrapper__mobile"
          >
            <Input
              style={{ width: '100%' }}
              label={t('Search for an address or user')}
              icon={<span className="material-icons">search</span>}
              rightIcon={
                searchValue && (
                  <span
                    className="material-icons"
                    onClick={clearInput}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        clearInput();
                      }
                    }}
                    role="button"
                    tabIndex={0}
                    style={{ cursor: 'pointer' }}
                  >
                    close
                  </span>
                )
              }
              value={searchValue}
              onChange={handleInputChange}
            />
          </div>

          <div
            className="hidden md:flex"
            style={{
              background: colors['greyscale-200'],
              height: '32px',
              width: '1px',
            }}
          ></div>

          <div
            className="block md:hidden"
            style={{ marginBottom: '10px' }}
          ></div>

          <div>
            {mailDomain?.abilities.post ? (
              <Button
                data-testid="button-new-mailbox"
                aria-label={t('Create a mailbox in {{name}} domain', {
                  name: mailDomain?.name,
                })}
                disabled={!canCreateMailbox}
                onClick={() => setIsCreateMailboxFormVisible(true)}
              >
                {t('New mail address')}
              </Button>
            ) : (
              <Tooltip content={t("You don't have the correct access right")}>
                <div>
                  <Button
                    data-testid="button-new-mailbox"
                    onClick={openModal}
                    disabled={!isCreateMailboxFormVisible}
                  >
                    {t('New mail address')}
                  </Button>
                </div>
              </Tooltip>
            )}
          </div>
        </div>

        <MailBoxesListView mailDomain={mailDomain} querySearch={searchValue} />
        {!mailDomain.count_mailboxes && (
          <Text $align="center" $size="small">
            {t('No mail box was created with this mail domain.')}
          </Text>
        )}
        {isCreateMailboxFormVisible && mailDomain ? (
          <ModalCreateMailbox
            mailDomain={mailDomain}
            closeModal={() => setIsCreateMailboxFormVisible(false)}
          />
        ) : null}
      </div>
    </>
  );

  // return isLoading ? (
  //   <Box $align="center" $justify="center" $height="100%">
  //     <Loader />
  //   </Box>
  // ) : (
  //   <>
  //     {isCreateMailboxFormVisible && mailDomain ? (
  //       <ModalCreateMailbox
  //         mailDomain={mailDomain}
  //         closeModal={() => setIsCreateMailboxFormVisible(false)}
  //       />
  //     ) : null}

  //     <TopBanner
  //       mailDomain={mailDomain}
  //       showMailBoxCreationForm={setIsCreateMailboxFormVisible}
  //     />

  //     <Card
  //       $overflow="auto"
  //       aria-label="Mailboxes list card"
  //       $css={`

  //         & table td:last-child {
  //           text-align: right;
  //         }
  //     `}
  //     >
  //       {error && <TextErrors causes={error.cause} />}

  //       <DataGrid
  //         aria-label="listbox"
  //         columns={[
  //           {
  //             field: 'name',
  //             headerName: t('Names'),
  //             renderCell: ({ row }) => (
  //               <Text
  //                 $weight="bold"
  //                 $theme="primary"
  //                 $css="text-transform: capitalize;"
  //               >
  //                 {row.name}
  //               </Text>
  //             ),
  //           },
  //           {
  //             field: 'email',
  //             headerName: t('Emails'),
  //           },
  //           {
  //             field: 'status',
  //             headerName: t('Status'),
  //           },
  //           {
  //             id: 'column-actions',
  //             renderCell: ({ row }) => (
  //               <MailDomainsActions
  //                 mailbox={row.mailbox}
  //                 mailDomain={mailDomain}
  //               />
  //             ),
  //           },
  //         ]}
  //         rows={viewMailboxes}
  //         isLoading={isLoading}
  //         onSortModelChange={setSortModel}
  //         sortModel={sortModel}
  //         pagination={{
  //           ...pagination,
  //           displayGoto: false,
  //         }}
  //         hideEmptyPlaceholderImage={true}
  //         emptyPlaceholderLabel={t(
  //           'No mail box was created with this mail domain.',
  //         )}
  //       />
  //     </Card>
  //   </>
  // );
}

// const TopBanner = ({
//   mailDomain,
//   showMailBoxCreationForm,
// }: {
//   mailDomain: MailDomain;
//   showMailBoxCreationForm: (value: boolean) => void;
// }) => {
//   const { t } = useTranslation();
//   const canCreateMailbox =
//     mailDomain.status === 'enabled' || mailDomain.status === 'pending';

//   const [isCreateMailboxFormVisible, setIsCreateMailboxFormVisible] =
//     useState(false);

//   return (
//     <Box $direction="column" $gap="1rem">
//       <AlertStatus status={mailDomain.status} />
//       <Box
//         $direction="row"
//         $justify="flex-end"
//         $margin={{ bottom: 'small' }}
//         $align="center"
//       >
//         <Box $display="flex" $direction="row">
//           {mailDomain?.abilities.post && (
//             <Button
//               aria-label={t('Create a mailbox in {{name}} domain', {
//                 name: mailDomain?.name,
//               })}
//               disabled={!canCreateMailbox}
//               onClick={() => setIsCreateMailboxFormVisible(true)}
//             >
//               {t('Create a mailbox')}
//             </Button>
//           )}
//         </Box>
//       </Box>
//     </Box>
//   );
// };

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
                'The domain name encounters an error. Please contact our support team to solve the problem: ',
              )}
              <a href="mailto:suiteterritoriale@anct.gouv.fr">
                suiteterritoriale@anct.gouv.fr
              </a>
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
