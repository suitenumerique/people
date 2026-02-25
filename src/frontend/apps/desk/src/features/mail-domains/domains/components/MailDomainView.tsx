import { Button } from '@gouvfr-lasuite/cunningham-react';
import { useRouter } from 'next/navigation';
import * as React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, CustomTabs, Icon, Tag, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { AliasesView } from '@/features/mail-domains/aliases';
import { useAliases } from '@/features/mail-domains/aliases/api/useAliases';
import {
  MailDomain,
  MailDomainAccessesAction,
  MailDomainLogoCircle,
  ModalRequiredActionDomain,
  Role,
} from '@/features/mail-domains/domains';
import { MailBoxesView } from '@/features/mail-domains/mailboxes';
import { useMailboxes } from '@/features/mail-domains/mailboxes/api/useMailboxes';

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

  const { data: mailboxesData } = useMailboxes({
    mailDomainSlug: mailDomain.slug,
    page: 1,
  });
  const { data: aliasesData } = useAliases({
    mailDomainSlug: mailDomain.slug,
    page: 1,
  });

  const countMailboxes = mailboxesData?.count ?? 0;
  const countAliases =
    aliasesData?.results.filter(
      (alias, index, self) =>
        index === self.findIndex((a) => a.local_part === alias.local_part),
    ).length ?? 0;

  const handleShowModal = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <>
      <Box aria-label="Mail Domains panel" className="container">
        <Box
          $padding={{ horizontal: 'md' }}
          $background="white"
          $justify="space-between"
          className="regie__panel__container"
        >
          <Box $direction="row"  $justify="space-between" $align="center">
            <Box $direction="row" $align="center" $gap="8px">
            <Button
              onClick={() => router.push('/mail-domains/')}
              icon={<span className="material-icons">arrow_back</span>}
              iconPosition="left"
              theme="tertiary"
              variant="bordered"
              style={{
                fontWeight: '500',
                marginRight: '12px',
              }}
            >
              {t('Domains')}
            </Button>
            <MailDomainLogoCircle size={24} />
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

            <MailDomainAccessesAction
              mailDomain={mailDomain}
              currentRole={currentRole}
              onConfigureDomain={handleShowModal}
            />

          </Box>
          <CustomTabs
            fullWidth={true}
            theme="neutral"
            tabs={[
              {
                id: 'mailboxes',
                label: t('Email addresses') + ` (${countMailboxes})`,
                iconName: 'mail',
                content: <MailBoxesView mailDomain={mailDomain} />,
              },
              {
                id: 'aliases',
                label: t('Aliases') + ` (${countAliases})`,
                iconName: 'forward_to_inbox',
                content: <AliasesView mailDomain={mailDomain} />,
              },
            ]}
          />

        </Box>

        {showModal && (
          <ModalRequiredActionDomain
            mailDomain={mailDomain}
            onMailDomainUpdate={onMailDomainUpdate ?? (() => {})}
            closeModal={closeModal}
          />
        )}
      </Box>
    </>
  );
};
