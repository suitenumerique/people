import {
  Button,
} from '@openfun/cunningham-react';
import { useCunninghamTheme } from '@/cunningham';

import * as React from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text, Tag } from '@/components';
import { AccessesContent } from '@/features/mail-domains/access-management';
import MailDomainsLogo from '@/features/mail-domains/assets/mail-domains-logo.svg';
import { MailDomain, Role, ModalRequiredActionDomain } from '@/features/mail-domains/domains';
import { MailBoxesLayout } from '@/features/mail-domains/mailboxes';
import { useFetchFromDimail } from '../api/useFetchMailDomain';

type Props = {
  mailDomain: MailDomain;
  onMailDomainUpdate?: (updatedDomain: MailDomain) => void;
};

export const MailDomainView = ({ mailDomain, onMailDomainUpdate }: Props) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();
  const [showModal, setShowModal] = React.useState(false);
  const currentRole = mailDomain.abilities.delete
    ? Role.OWNER
    : mailDomain.abilities.manage_accesses
      ? Role.ADMIN
      : Role.VIEWER;

  // const tabs = useMemo(() => {
  //   return [
  //     {
  //       ariaLabel: t('Go to mailbox management'),
  //       id: 'mails',
  //       iconName: 'mail',
  //       label: t('Mailbox management'),
  //       content: <MailDomainsContent mailDomain={mailDomain} />,
  //     },
  //     {
  //       ariaLabel: t('Go to accesses management'),
  //       id: 'accesses',
  //       iconName: 'people',
  //       label: t('Access management'),
  //       content: (
  //         <AccessesContent mailDomain={mailDomain} currentRole={currentRole} />
  //       ),
  //     },
  //   ];
  // }, [t, currentRole, mailDomain]);

  const handleShowModal = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <>
    <div
      aria-label="Mail Domains panel"
      className="container"
    >
      <Box 
        $padding={{ horizontal: 'md' }}
        $background="white"
        $align="center"
        $gap="8px"
        $radius="4px"
        $direction="row"
        $css={`
          border: 1px solid ${colorsTokens()['greyscale-200']};
        `}>
        <Button 
          href="/mail-domains"
          icon={<span 
          className="material-icons">arrow_back</span>}
          iconPosition="left"
          color="secondary"
          style={{
            fontWeight: '500'
          }}
          >
          {t('Domains')}
        </Button>
        <MailDomainsLogo aria-hidden="true" />
        <Text as="h5" $size="h5" $weight="bold" $theme="primary">
          {mailDomain.name}
        </Text>

        {(mailDomain?.status === 'pending' || mailDomain?.status === 'action_required') 
          && (<Box onClick={handleShowModal}>
          <Tag
          onClick={handleShowModal}
          showTooltip="true"
          status={mailDomain.status}
          tooltipType="domain"
          placement="bottom"
          ></Tag>
          </Box>
          )}

      </Box>

      {showModal && 
        <ModalRequiredActionDomain 
          mailDomain={mailDomain}
          onMailDomainUpdate={onMailDomainUpdate}
          closeModal={closeModal} />
      }

      <Box
        $padding={{ horizontal: 'md' }}
        $margin={{ top: 'md' }}
        $background="white"
        $align="center"
        $gap="8px"
        $radius="4px"
        $direction="row"
        $css={`
          border: 1px solid ${colorsTokens()['greyscale-200']};
        `}>
        
          <MailBoxesLayout mailDomain={mailDomain} />
      </Box>
      </div>
    </>
  );
};
