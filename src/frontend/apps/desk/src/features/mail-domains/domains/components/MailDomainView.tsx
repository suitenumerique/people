import {
  Button,
  usePagination
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
import { MailDomainAccessesAction } from '@/features/mail-domains/domains';
import { useMailDomainAccesses } from '@/features/mail-domains/access-management/api';

type Props = {
  mailDomain: MailDomain;
  currentRole: Role,
  onMailDomainUpdate?: (updatedDomain: MailDomain) => void;
};

export const MailDomainView = ({ mailDomain, currentRole, onMailDomainUpdate }: Props) => {
  const { t } = useTranslation();
  const pagination = usePagination({
    pageSize: 20,
  });
  const { colorsTokens } = useCunninghamTheme();
  const [showModal, setShowModal] = React.useState(false);
  const [accesses, setAccesses] = React.useState<Access[]>([]);
  const { page, pageSize, setPagesCount } = pagination;

  const { data, isLoading, error } = useMailDomainAccesses({
    slug: mailDomain.slug,
    page
  });

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
        $justify="space-between"
        $gap="8px"
        $align="center"
        $radius="4px"
        $direction="row"
        $css={`
          border: 1px solid ${colorsTokens()['greyscale-200']};
        `}>
        <Box $direction="row" $align="center" $gap="8px">
          <Button 
            href="/mail-domains"
            icon={<span 
            className="material-icons">
              arrow_back
              </span>}
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

          {(mailDomain?.status === 'pending' || mailDomain?.status === 'action_required' || mailDomain?.status) 
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
          <Box $align="center">
            <MailDomainAccessesAction mailDomain={mailDomain} currentRole={currentRole} />
          </Box>
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
