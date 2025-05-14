import { Button } from '@openfun/cunningham-react';
import { useRouter } from 'next/navigation';
import * as React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Tag, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import MailDomainsLogo from '@/features/mail-domains/assets/mail-domains-logo.svg';
import {
  MailDomain,
  MailDomainAccessesAction,
  ModalRequiredActionDomain,
  Role,
} from '@/features/mail-domains/domains';
import { MailBoxesView } from '@/features/mail-domains/mailboxes';

type Props = {
  mailDomain: MailDomain;
  currentRole: Role;
  onMailDomainUpdate?: (updatedDomain: MailDomain) => void;
};

export const MailDomainView = ({
  mailDomain,
  currentRole,
  onMailDomainUpdate,
}: Props) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();
  const router = useRouter();
  const [showModal, setShowModal] = React.useState(false);

  const handleShowModal = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <>
      <div aria-label="Mail Domains panel" className="container">
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
        `}
        >
          <Box $direction="row" $align="center" $gap="8px">
            <Button
              onClick={() => router.push('/mail-domains/')}
              icon={<span className="material-icons">arrow_back</span>}
              iconPosition="left"
              color="secondary"
              style={{
                fontWeight: '500',
              }}
            >
              {t('Domains')}
            </Button>
            <MailDomainsLogo aria-hidden="true" />
            <Text as="h5" $size="h5" $weight="bold" $theme="primary">
              {mailDomain.name}
            </Text>

            {(mailDomain?.status === 'pending' ||
              mailDomain?.status === 'action_required' ||
              mailDomain?.status) && (
              <button
                data-testid="actions_required"
                onClick={handleShowModal}
                style={{
                  backgroundColor: 'transparent',
                  border: 'none',
                }}
              >
                <Tag
                  showTooltip={true}
                  status={mailDomain.status}
                  tooltipType="domain"
                  placement="bottom"
                ></Tag>
              </button>
            )}
          </Box>
          <Box $align="center">
            <MailDomainAccessesAction
              mailDomain={mailDomain}
              currentRole={currentRole}
            />
          </Box>
        </Box>

        {showModal && (
          <ModalRequiredActionDomain
            mailDomain={mailDomain}
            onMailDomainUpdate={onMailDomainUpdate ?? (() => {})}
            closeModal={closeModal}
          />
        )}

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
        `}
        >
          <MailBoxesView mailDomain={mailDomain} />
        </Box>
      </div>
    </>
  );
};
