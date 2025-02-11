import { Modal, ModalSize } from '@openfun/cunningham-react';
import * as React from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { CustomTabs } from '@/components/tabs/CustomTabs';
import { AccessesContent } from '@/features/mail-domains/access-management';
import MailDomainsLogo from '@/features/mail-domains/assets/mail-domains-logo.svg';
import { MailDomain, Role } from '@/features/mail-domains/domains';
import { MailDomainsContent } from '@/features/mail-domains/mailboxes';

type Props = {
  mailDomain: MailDomain;
};
export const MailDomainView = ({ mailDomain }: Props) => {
  const { t } = useTranslation();
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
                ([check, value]) => (
                  <ul key={check}>
                    <li>
                      <b>{check}</b>: {value}
                    </li>
                  </ul>
                ),
              )}
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
