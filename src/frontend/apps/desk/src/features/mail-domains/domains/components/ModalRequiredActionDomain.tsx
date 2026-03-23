import {
  Button,
  Loader,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Icon, Text } from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';
import { MailDomain } from '@/features/mail-domains/domains';

import { useFetchFromDimail } from '../api/useFetchMailDomain';

export const ModalRequiredActionDomain = ({
  mailDomain,
  onMailDomainUpdate,
  closeModal,
}: {
  closeModal: () => void;
  mailDomain: MailDomain;
  onMailDomainUpdate: (updatedDomain: MailDomain) => void;
}) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();

  const { mutate: fetchMailDomain, isPending: fetchPending } =
    useFetchFromDimail({
      onSuccess: (data: MailDomain) => {
        closeModal();
        toast(t('Domain data fetched successfully'), VariantType.SUCCESS);
        onMailDomainUpdate?.(data);
      },
      onError: () => {
        toast(t('Failed to fetch domain data'), VariantType.ERROR);
      },
    });

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text);
    toast(t('copy done'), VariantType.SUCCESS);
  };

  const isActionRequired = mailDomain.status === 'action_required';
  const isEnabled = mailDomain.status === 'enabled';

  const title = isActionRequired
    ? t('Required actions on domain')
    : t('Domain configuration');

  const step = 0;

  const steps = [
    {
      title,
      content: (
        <Text>
          <span>
            {isActionRequired &&
              t(
                'The domain is currently in action required status. Please take the necessary actions to resolve those following issues.',
              )}
            {isEnabled &&
              t(
                'The domain is currently enabled and its configuration looks correct. You can run a new check to make sure everything is still properly configured.',
              )}
            {!isActionRequired &&
              !isEnabled &&
              t(
                'The domain status can be checked again to update its configuration details.',
              )}
          </span>
          {mailDomain.action_required_details && (
            <>
              {isActionRequired && (
                <>
                  <h3>{t('Actions required detail')}</h3>

                  <div>
                    {Object.entries(mailDomain.action_required_details).map(
                      ([check, value], index) => (
                        <ul key={`action-required-list-${index}`}>
                          <li key={`action-required-${index}`}>
                            <b>{check}</b>: {value}
                          </li>
                        </ul>
                      ),
                    )}
                  </div>
                </>
              )}
            </>
          )}
          {mailDomain.expected_config && (
            <Box $margin={{ bottom: 'medium' }}>
              <h3>
                {mailDomain.status === 'action_required'
                  ? t('DNS Configuration Required:')
                  : t('DNS Configuration:')}
              </h3>
              <div>
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
                        <span
                          style={{
                            backgroundColor: '#000',
                            color: '#fff',
                            padding: '10px',
                            display: 'block',
                            borderRadius: '5px',
                            fontFamily: 'monospace',
                          }}
                        >
                          {item.value}
                        </span>
                        <button
                          style={{
                            padding: '2px 5px',
                            backgroundColor: '#999',
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
              </div>
            </Box>
          )}
        </Text>
      ),
      rightAction: fetchPending ? (
        <Loader />
      ) : (
        <Button
          color="brand"
          variant="primary"
          onClick={() => {
            void fetchMailDomain(mailDomain.slug);
          }}
          icon={<Icon iconName="refresh" $theme="gray" $variation="000" />}
        >
          {t('Re-run check')}
        </Button>
      ),
      leftAction: (
        <Button color="neutral" variant="secondary" onClick={closeModal}>
          {t('Close')}
        </Button>
      ),
    },
  ];

  return (
    <CustomModal
      isOpen
      step={step}
      totalSteps={steps.length}
      leftActions={steps[step].leftAction}
      hideCloseButton={true}
      closeOnClickOutside={true}
      onClose={closeModal}
      closeOnEsc
      rightActions={steps[step].rightAction}
      size={ModalSize.MEDIUM}
      title={steps[step].title}
    >
      <Box $padding="md">{steps[step].content}</Box>
    </CustomModal>
  );
};
