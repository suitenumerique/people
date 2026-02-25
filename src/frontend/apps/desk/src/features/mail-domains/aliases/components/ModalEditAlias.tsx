import {
  Button,
  Loader,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { parseAPIError } from '@/api/parseAPIError';
import {
  Box,
  HorizontalSeparator,
  Icon,
  LocalInput,
  Text,
  TextErrors,
} from '@/components';
import { Modal } from '@/components/Modal';
import { CustomModal } from '@/components/modal/CustomModal';

import { MailDomain } from '../../domains/types';
import { useCreateAlias } from '../api/useCreateAlias';
import { useDeleteAlias } from '../api/useDeleteAlias';
import { useDeleteAliasById } from '../api/useDeleteAliasById';
import { AliasGroup } from '../types';

const FORM_ID = 'form-edit-alias';

export const ModalEditAlias = ({
  mailDomain,
  aliasGroup,
  closeModal,
}: {
  mailDomain: MailDomain;
  aliasGroup: AliasGroup;
  closeModal: () => void;
}) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const [errorCauses, setErrorCauses] = useState<string[]>([]);
  const [step] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [destinations, setDestinations] = useState<string[]>([]);
  const [newDestination, setNewDestination] = useState('');
  const [destinationError, setDestinationError] = useState<string | undefined>(
    undefined,
  );
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
  }>({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {},
  });

  useEffect(() => {
    setDestinations([...aliasGroup.destinations]);
  }, [aliasGroup]);

  const addDestination = async () => {
    const trimmed = newDestination.trim();
    if (!trimmed) {
      setDestinationError(t('Please enter an email address'));
      return;
    }

    // Valid email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      setDestinationError(t('Please enter a valid email address'));
      return;
    }

    // Email already in list
    if (destinations.includes(trimmed)) {
      setDestinationError(t('This email address is already in the list'));
      return;
    }

    // Check domain enabled
    if (mailDomain.status !== 'enabled') {
      setDestinationError(
        t(
          'The domain must be enabled to add destinations. Current status: {{status}}',
          {
            status: mailDomain.status,
          },
        ),
      );
      return;
    }

    setIsSubmitting(true);
    setDestinationError(undefined);

    try {
      await new Promise<void>((resolve, reject) => {
        createAlias(
          {
            local_part: aliasGroup.local_part,
            destination: trimmed,
            mailDomainSlug: mailDomain.slug,
          },
          {
            onSuccess: () => {
              toast(t('Destination added successfully'), VariantType.SUCCESS, {
                duration: 4000,
              });
              setDestinations([...destinations, trimmed]);
              setNewDestination('');
              resolve();
            },
            onError: (error) => {
              const causes =
                parseAPIError({
                  error,
                  errorParams: [
                    [
                      ['Local part ".*" already used by a mailbox.'],
                      t('This email prefix is already used by a mailbox.'),
                      undefined,
                    ],
                    [
                      ['Invalid format'],
                      t('Invalid format for the email prefix.'),
                      undefined,
                    ],
                  ],
                  serverErrorParams: [
                    t(
                      'The domain must be enabled to add destinations. Please check the domain status.',
                    ),
                    undefined,
                  ],
                }) || [];

              if (causes.length > 0) {
                setDestinationError(causes[0]);
              } else {
                setDestinationError(
                  t('Failed to add destination. Please try again.'),
                );
              }
              reject(error);
            },
          },
        );
      });
    } catch {
    } finally {
      setIsSubmitting(false);
    }
  };

  const removeDestination = (destination: string) => {
    setConfirmModal({
      isOpen: true,
      title: t('Remove destination'),
      message: t(
        'Are you sure you want to remove {{destination}} from this alias?',
        { destination },
      ),
      onConfirm: () => {
        setConfirmModal({ ...confirmModal, isOpen: false });
        void handleRemoveDestination(destination);
      },
    });
  };

  const handleRemoveDestination = async (destination: string) => {
    setIsSubmitting(true);

    const aliasId = aliasGroup.destinationIds[destination];
    if (!aliasId) {
      toast(
        t('Failed to find alias ID for this destination'),
        VariantType.ERROR,
        {
          duration: 4000,
        },
      );
      setIsSubmitting(false);
      return;
    }

    try {
      await new Promise<void>((resolve, reject) => {
        deleteAliasById(
          {
            mailDomainSlug: mailDomain.slug,
            aliasId,
          },
          {
            onSuccess: () => {
              toast(
                t('Destination removed successfully'),
                VariantType.SUCCESS,
                {
                  duration: 4000,
                },
              );
              setDestinations(destinations.filter((d) => d !== destination));
              resolve();
              closeModal();
            },
            onError: (error) => {
              const causes =
                parseAPIError({
                  error,
                  errorParams: [],
                  serverErrorParams: [
                    t(
                      'An error occurred while removing the destination. Please try again.',
                    ),
                    undefined,
                  ],
                }) || [];

              if (causes.length > 0) {
                setDestinationError(causes[0]);
              } else {
                toast(t('Failed to remove destination'), VariantType.ERROR, {
                  duration: 4000,
                });
              }
              reject(error);
            },
          },
        );
      });
    } catch {
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemoveAllDestinations = () => {
    setConfirmModal({
      isOpen: true,
      title: t('Delete this alias'),
      message: t(
        'Are you sure you want to remove all destinations from this alias? This action cannot be undone.',
      ),
      onConfirm: () => {
        setConfirmModal({ ...confirmModal, isOpen: false });
        void removeAllDestinations();
      },
    });
  };

  const removeAllDestinations = async () => {
    if (destinations.length === 0) {
      return;
    }

    setIsSubmitting(true);
    setErrorCauses([]);

    try {
      await new Promise<void>((resolve, reject) => {
        deleteAlias(
          {
            mailDomainSlug: mailDomain.slug,
            localPart: aliasGroup.local_part,
          },
          {
            onSuccess: () => {
              toast(t('Alias deleted successfully'), VariantType.SUCCESS, {
                duration: 4000,
              });
              setDestinations([]);
              resolve();
              closeModal();
            },
            onError: (error) => {
              const causes =
                parseAPIError({
                  error,
                  errorParams: [],
                  serverErrorParams: [
                    t(
                      'An error occurred while deleting the alias. Please try again.',
                    ),
                    undefined,
                  ],
                }) || [];

              if (causes.length > 0) {
                setErrorCauses(causes);
              } else {
                toast(t('Failed to delete alias'), VariantType.ERROR, {
                  duration: 4000,
                });
              }
              reject(error);
            },
          },
        );
      });
    } catch {
    } finally {
      setIsSubmitting(false);
    }
  };

  const { mutate: createAlias } = useCreateAlias({
    mailDomainSlug: mailDomain.slug,
  });

  const { mutate: deleteAliasById } = useDeleteAliasById();
  const { mutate: deleteAlias } = useDeleteAlias();

  const steps = [
    {
      title: t('Manage alias'),
      content: (
        <>
          {!!errorCauses.length && <TextErrors causes={errorCauses} />}
          <form
            id={FORM_ID}
            onSubmit={(e) => {
              e.preventDefault();
              void addDestination();
            }}
          >
            <Box $padding={{ top: 'sm', horizontal: 'md' }} $gap="4px">
              <Text $size="md" $weight="bold">
                {t('Alias configuration')}
              </Text>
              <Text $theme="gray" $variation="600">
                {t('Manage the destination email addresses for this alias.')}
              </Text>
            </Box>

            <Box $padding="md">
              <LocalInput
                id="edit-alias-local-part"
                label={t('Name of the alias')}
                value={aliasGroup.local_part}
                right={
                  <span
                    style={{
                      padding: '12px 12px 12px 0',
                      fontSize: 14,
                      color: 'var(--c--theme--colors--gray-550)',
                      fontWeight: 500,
                    }}
                  >
                    @{mailDomain.name}
                  </span>
                }
                required={false}
                readOnly
                disabled
              />
            </Box>

            <HorizontalSeparator $withPadding={true} />

            <Box $padding={{ horizontal: 'md' }}>
              <Box $margin={{ top: 'base', bottom: 'base' }} $gap="12px">
                <Text $size="sm" $weight="500">
                  {t('Destination email addresses')}
                </Text>

                <Box $gap="4px">
                  <Box $direction="column" $gap="8px">
                    <Box $margin={{ bottom: 'xxs' }}>
                      <Text $size="sm" $weight="500">
                        {t('Add destination email')}
                      </Text>
                    </Box>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        width: '100%',
                        flexDirection: 'row',
                        flexWrap: 'nowrap',
                        border:
                          '1px solid var(--c--contextuals--border--semantic--neutral--tertiary)',
                        borderRadius: 4,
                        overflow: 'hidden',
                        paddingRight: '4px',
                      }}
                    >
                      <input
                        id="edit-new-destination"
                        value={newDestination}
                        onChange={(e) => {
                          setNewDestination(e.target.value);
                          setDestinationError(undefined);
                        }}
                        onKeyUp={(e) => {
                          if (e.key === 'Enter') {
                            void addDestination();
                          }
                        }}
                        style={{
                          flex: '1 1 0',
                          minWidth: 0,
                          padding: '12px',
                          border: 'none',
                          borderRadius: 0,
                          fontSize: 14,
                          background: 'transparent',
                          color:
                            'var(--c--contextuals--text--semantic--neutral--primary)',
                          outline: 'none',
                        }}
                        placeholder={t('john.appleseed@example.fr')}
                      />
                      <Button
                        type="submit"
                        size="small"
                        form={FORM_ID}
                        disabled={!newDestination.trim() || isSubmitting}
                        tabIndex={-1}
                        icon={<Icon iconName="add" $color="currentColor" />}
                      >
                        {isSubmitting ? t('Adding...') : t('Add destination')}
                      </Button>
                    </div>
                  </Box>
                  {destinationError && (
                    <Text $theme="error" $variation="secondary" $size="sm">
                      {destinationError}
                    </Text>
                  )}
                </Box>

                {/* Tableau des destinations */}
                {destinations.length > 0 && (
                  <Box
                    $margin={{ top: 'md' }}
                    style={{
                      border:
                        '1px solid var(--c--contextuals--border--surface--primary)',
                      borderRadius: '4px',
                      overflow: 'hidden',
                    }}
                  >
                    <table
                      style={{ width: '100%', borderCollapse: 'collapse' }}
                    >
                      <thead>
                        <tr
                          style={{
                            paddingBottom: '12px',
                            borderBottom:
                              '1px solid var(--c--contextuals--border--surface--primary)',
                          }}
                        >
                          <th
                            style={{
                              paddingLeft: '12px',
                              textAlign: 'left',
                              fontWeight: 500,
                              fontSize: '14px',
                            }}
                          >
                            {t('Email address')}
                          </th>
                          <th
                            style={{
                              paddingRight: '12px',
                              textAlign: 'right',
                              fontWeight: 500,
                              width: '80px',
                            }}
                          >
                            {t('Actions')}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {destinations.map((destination, index) => (
                          <tr
                            key={index}
                            style={{
                              borderBottom:
                                index < destinations.length - 1
                                  ? '1px solid var(--c--contextuals--border--surface--primary)'
                                  : 'none',
                            }}
                          >
                            <td>
                              <Text $size="sm" $padding={{ left: '12px' }}>
                                {destination}
                              </Text>
                            </td>
                            <td style={{ textAlign: 'right', padding: '12px' }}>
                              <Button
                                type="button"
                                size="small"
                                color="neutral"
                                variant="tertiary"
                                onClick={() => removeDestination(destination)}
                                aria-label={t('Remove destination')}
                                icon={<Icon iconName="delete" />}
                                disabled={isSubmitting}
                              />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                )}
              </Box>
            </Box>
          </form>
        </>
      ),
      leftAction: (
        <Button color="neutral" variant="secondary" onClick={closeModal}>
          {t('Close')}
        </Button>
      ),
      rightAction: (
        <Box $direction="row" $gap="6px">
          {destinations.length > 0 && (
            <Button
              type="button"
              color="error"
              onClick={handleRemoveAllDestinations}
              disabled={isSubmitting}
              icon={<Icon iconName="delete" $theme="gray" $variation="000" />}
            >
              {t('Delete this alias')}
            </Button>
          )}
        </Box>
      ),
    },
  ];

  return (
    <div id="modal-edit-alias">
      <CustomModal
        isOpen
        hideCloseButton
        step={step}
        totalSteps={steps.length}
        leftActions={steps[step].leftAction}
        rightActions={steps[step].rightAction}
        size={ModalSize.MEDIUM}
        title={steps[step].title}
        onClose={closeModal}
        closeOnEsc
        closeOnClickOutside
      >
        {steps[step].content}
        {isSubmitting && (
          <Box $align="center" $padding="md">
            <Loader />
            <Text $theme="gray" $variation="600" $margin={{ top: 'sm' }}>
              {t('Updating alias...')}
            </Text>
          </Box>
        )}
      </CustomModal>

      {/* Confirmation Modal */}
      <Modal
        isOpen={confirmModal.isOpen}
        closeOnClickOutside
        hideCloseButton
        leftActions={
          <Button
            color="neutral"
            variant="secondary"
            fullWidth
            onClick={() => setConfirmModal({ ...confirmModal, isOpen: false })}
          >
            {t('Cancel')}
          </Button>
        }
        rightActions={
          <Button
            color="error"
            fullWidth
            onClick={confirmModal.onConfirm}
            disabled={isSubmitting}
          >
            {t('Confirm')}
          </Button>
        }
        size={ModalSize.MEDIUM}
        title={confirmModal.title}
        onClose={() => setConfirmModal({ ...confirmModal, isOpen: false })}
      >
        <Box $padding="md">
          <Text>{confirmModal.message}</Text>
        </Box>
      </Modal>
    </div>
  );
};
