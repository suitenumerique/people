import {
  Button,
  Loader,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
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

  const step = 0;

  const steps = [
    {
      title: t('Required actions on domain'),
      content: (
        <Text>
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
        </Text>
      ),
      rightAction: fetchPending ? (
        <Loader />
      ) : (
        <Button
          onClick={() => {
            void fetchMailDomain(mailDomain.slug);
          }}
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
