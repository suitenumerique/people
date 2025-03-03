import {
  Button,
  Loader,
  Modal,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import * as React from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { CustomTabs } from '@/components/tabs/CustomTabs';
import { AccessesContent } from '@/features/mail-domains/access-management';
import MailDomainsLogo from '@/features/mail-domains/assets/mail-domains-logo.svg';
import { MailDomain, Role } from '@/features/mail-domains/domains';
import { MailDomainsContent } from '@/features/mail-domains/mailboxes';

import { useFetchFromDimail } from '../api/useFetchMailDomain';

type Props = {
  mailDomain: MailDomain;
  onMailDomainUpdate?: (updatedDomain: MailDomain) => void;
};

export const MailDomainView = ({ mailDomain, onMailDomainUpdate }: Props) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const [showModal, setShowModal] = React.useState(false);
  const currentRole = mailDomain.abilities.delete
    ? Role.OWNER
    : mailDomain.abilities.manage_accesses
      ? Role.ADMIN
      : Role.VIEWER;

  const tabs = useMemo(() => {
    return [
      {
        ariaLabel: t('Go to mailbox management'),
        id: 'mails',
        iconName: 'mail',
        label: t('Mailbox management'),
        content: <MailDomainsContent mailDomain={mailDomain} />,
      },
      {
        ariaLabel: t('Go to accesses management'),
        id: 'accesses',
        iconName: 'people',
        label: t('Access management'),
        content: (
          <AccessesContent mailDomain={mailDomain} currentRole={currentRole} />
        ),
      },
    ];
  }, [t, currentRole, mailDomain]);

  const handleShowModal = () => {
    setShowModal(true);
  };
  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text);
    toast(t('copy done'), VariantType.SUCCESS);
  };

  const { mutate: fetchMailDomain, isPending: fetchPending } =
    useFetchFromDimail({
      onSuccess: (data: MailDomain) => {
        setShowModal(false);
        toast(t('Domain data fetched successfully'), VariantType.SUCCESS);
        onMailDomainUpdate?.(data);
      },
      onError: () => {
        toast(t('Failed to fetch domain data'), VariantType.ERROR);
      },
    });

  return (
    <>
      {showModal && (
        <Modal
          isOpen
          size={ModalSize.EXTRA_LARGE}
          onClose={() => setShowModal(false)}
          title={t('Required actions on domain')}
        >
          <p>
            {t(
              'The domain is currently in action required status. Please take the necessary actions to resolve those following issues.',
            )}
          </p>
          <h3>{t('Actions required detail')}</h3>

          <pre>
            {mailDomain.action_required_details &&
              Object.entries(mailDomain.action_required_details).map(
                ([check, value], index) => (
                  <ul key={`action-required-list-${index}`}>
                    <li key={`action-required-${index}`}>
                      <b>{check}</b>: {value}
                    </li>
                  </ul>
                ),
              )}
          </pre>
          {mailDomain.expected_config && (
            <Box $margin={{ bottom: 'medium' }}>
              <h3>{t('DNS Configuration Required:')}</h3>
              <pre>
                <div
                  style={{
                    whiteSpace: 'pre-wrap',
                    overflowWrap: 'break-word',
                  }}
                >
                  {t('Add the following DNS values:')}
                  <ul>
                    {mailDomain.expected_config.map((item, index) => (
                      <li
                        key={`dns-record-${index}`}
                        style={{ marginBottom: '10px' }}
                      >
                        {item.target && (
                          <>
                            <b>{item.target.toUpperCase()}</b> -{' '}
                          </>
                        )}
                        <b>{item.type.toUpperCase()}</b> {t('with value:')}{' '}
                        <span style={{ backgroundColor: '#d4e5f5' }}>
                          {item.value}
                        </span>
                        <button
                          style={{
                            padding: '2px 5px',
                            marginLeft: '10px',
                            backgroundColor: '#cccccc',
                            border: 'none',
                            color: 'white',
                            cursor: 'pointer',
                            fontWeight: '500',
                            borderRadius: '5px',
                          }}
                          onClick={() => {
                            void copyToClipboard(item.value);
                          }}
                        >
                          {t('Copy')}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              </pre>
            </Box>
          )}
          <pre>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              {fetchPending ? (
                <Loader />
              ) : (
                <Button
                  onClick={() => {
                    void fetchMailDomain(mailDomain.slug);
                  }}
                >
                  {t('Re-run check')}
                </Button>
              )}
            </div>
          </pre>
        </Modal>
      )}
      <Box $padding="big">
        <Box
          $width="100%"
          $direction="row"
          $align="center"
          $gap="2.25rem"
          $justify="center"
        >
          <Box
            $direction="row"
            $justify="center"
            $margin={{ bottom: 'big' }}
            $gap="0.5rem"
          >
            <MailDomainsLogo aria-hidden="true" />
            <Text $margin="none" as="h3" $size="h3">
              {mailDomain?.name}
            </Text>
            {/* TODO: remove when pending status will be removed */}
            {mailDomain?.status === 'pending' && (
              <button
                onClick={handleShowModal}
                style={{
                  padding: '5px 10px',
                  marginLeft: '10px',
                  backgroundColor: '#cccccc',
                  border: 'none',
                  color: 'white',
                  cursor: 'pointer',
                  fontWeight: '500',
                  borderRadius: '5px',
                }}
                data-modal="mail-domain-status"
              >
                {t('Pending')}
              </button>
            )}
            {mailDomain?.status === 'action_required' && (
              <button
                onClick={handleShowModal}
                style={{
                  padding: '5px 10px',
                  marginLeft: '10px',
                  backgroundColor: '#f37802',
                  border: 'none',
                  color: 'white',
                  cursor: 'pointer',
                  fontWeight: '500',
                  borderRadius: '5px',
                }}
                data-modal="mail-domain-status"
              >
                {t('Actions required')}
              </button>
            )}
          </Box>
        </Box>
        <CustomTabs tabs={tabs} />
      </Box>
    </>
  );
};
