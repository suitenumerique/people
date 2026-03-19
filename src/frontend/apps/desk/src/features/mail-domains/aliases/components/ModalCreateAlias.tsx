import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import { standardSchemaResolver } from '@hookform/resolvers/standard-schema';
import React, { useState } from 'react';
import { Controller, FormProvider, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { parseAPIError } from '@/api/parseAPIError';
import {
  Box,
  HorizontalSeparator,
  Icon,
  LocalInput,
  Text,
  TextErrors,
} from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';

import { MailDomain } from '../../domains/types';
import { useCreateAlias } from '../api';

const FORM_ID = 'form-create-alias';

export const ModalCreateAlias = ({
  mailDomain,
  closeModal,
}: {
  mailDomain: MailDomain;
  closeModal: () => void;
}) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const [errorCauses, setErrorCauses] = useState<string[]>([]);
  const [step] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [destinations, setDestinations] = useState<string[]>([]);
  const [newDestination, setNewDestination] = useState<string>('');
  const [destinationError, setDestinationError] = useState<string | null>(null);

  type AliasFormData = {
    local_part: string;
  };

  const createAliasValidationSchema: z.ZodType<AliasFormData> = z.object({
    local_part: z
      .string()
      .regex(/^((?!@|\s)([a-zA-Z0-9.\-]))*$/, t('Invalid format'))
      .min(1, t('You must have minimum 1 character')),
  });

  const methods = useForm<AliasFormData>({
    resolver: standardSchemaResolver(createAliasValidationSchema),
    defaultValues: {
      local_part: '',
    },
    mode: 'onChange',
  });

  const addDestination = () => {
    const trimmed = newDestination?.toString().trim();
    if (!trimmed) {
      setDestinationError(t('Please enter an email address'));
      return;
    }

    // Validation email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      setDestinationError(t('Please enter a valid email address'));
      return;
    }

    // Vérifier si déjà présent
    if (destinations.includes(trimmed)) {
      setDestinationError(t('This email address is already in the list'));
      return;
    }

    setDestinations([...destinations, trimmed]);
    setNewDestination('');
    setDestinationError(null);
  };

  const removeDestination = (index: number) => {
    setDestinations(destinations.filter((_, i) => i !== index));
  };

  const { mutate: createAlias } = useCreateAlias({
    mailDomainSlug: mailDomain.slug,
  });

  const onSubmitCallback = async (event: React.FormEvent) => {
    event.preventDefault();
    const isValid = await methods.trigger();
    if (!isValid) {
      return;
    }

    if (destinations.length === 0) {
      toast(t('Please add at least one destination email'), VariantType.ERROR, {
        duration: 4000,
      });
      return;
    }

    const data = methods.getValues();

    setIsSubmitting(true);
    setErrorCauses([]);

    let successCount = 0;
    let errorCount = 0;
    const allErrors: string[] = [];

    for (const destination of destinations) {
      try {
        await new Promise<void>((resolve, reject) => {
          createAlias(
            {
              local_part: data.local_part,
              destination: destination.trim(),
              mailDomainSlug: mailDomain.slug,
            },
            {
              onSuccess: () => {
                successCount++;
                resolve();
              },
              onError: (error) => {
                errorCount++;
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
                        'The domain must be enabled to create aliases. Please check the domain status.',
                      ),
                      undefined,
                    ],
                  }) || [];

                if (causes.length > 0) {
                  allErrors.push(...causes);
                }

                reject(error);
              },
            },
          );
        });
      } catch {
        // Erreur déjà gérée dans onError
      }
    }

    setIsSubmitting(false);

    // Afficher les résultats
    if (errorCount > 0) {
      setErrorCauses(allErrors);
    }

    if (successCount === destinations.length) {
      toast(
        t('All {{count}} alias(es) created successfully!', {
          count: successCount,
        }),
        VariantType.SUCCESS,
        { duration: 4000 },
      );
      closeModal();
    } else if (successCount > 0) {
      toast(
        t('{{success}} alias(es) created, {{errors}} failed', {
          success: successCount,
          errors: errorCount,
        }),
        VariantType.WARNING,
        { duration: 5000 },
      );
    } else {
      toast(t('Failed to create aliases'), VariantType.ERROR, {
        duration: 4000,
      });
    }
  };

  const steps = [
    {
      title: t('New alias'),
      content: (
        <FormProvider {...methods}>
          {!!errorCauses.length && <TextErrors causes={errorCauses} />}
          <form
            id={FORM_ID}
            onSubmit={(e) => {
              void onSubmitCallback(e);
            }}
          >
            <Box $padding={{ top: 'sm', horizontal: 'md' }} $gap="4px">
              <Text $size="md" $weight="bold">
                {t('Alias configuration')}
              </Text>
              <Text $theme="gray" $variation="600">
                {t(
                  'An alias allows you to redirect emails to one or more addresses.',
                )}
              </Text>
            </Box>

            <Box $padding="md">
              <Controller
                name="local_part"
                control={methods.control}
                render={({ field, fieldState }) => (
                  <LocalInput
                    {...field}
                    id="alias_local_part"
                    label={t('Name of the alias')}
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
                    required
                    error={fieldState.error?.message}
                  />
                )}
              />
            </Box>

            <HorizontalSeparator $withPadding={true} />

            <Box $padding={{ horizontal: 'md' }}>
              <Box $margin={{ top: 'base', bottom: 'base' }} $gap="12px">
                <Box $gap="4px">
                  <Box $direction="column" $gap="8px">
                    <Box $margin={{ bottom: 'xxs' }}>
                      <label
                        htmlFor="newDestination"
                        style={{
                          fontWeight: 500,
                          color:
                            'var(--c--contextuals--text--semantic--neutral--primary)',
                        }}
                      >
                        {t('Add destination email')}
                      </label>
                    </Box>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        width: '100%',
                        flexDirection: 'row',
                        flexWrap: 'nowrap',
                        border: `1px solid var(--c--contextuals--border--semantic--neutral--tertiary)`,
                        borderRadius: 4,
                        overflow: 'hidden',
                        paddingRight: '4px',
                      }}
                    >
                      <input
                        id="newDestination"
                        aria-required="true"
                        required
                        onChange={(e) => {
                          setNewDestination(e.target.value);
                          setDestinationError(null);
                        }}
                        onKeyUp={(e) => {
                          if (e.key === 'Enter') {
                            addDestination();
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
                            'var(--c--contextuals--text--semantic--neutral--tertiary)',
                          outline: 'none',
                        }}
                      />
                      <Button
                        type="button"
                        size="small"
                        onClick={addDestination}
                        disabled={!newDestination.trim()}
                        tabIndex={-1}
                        icon={<Icon iconName="add" $color="currentColor" />}
                      >
                        {t('Add destination')}
                      </Button>
                    </div>
                  </Box>
                  {destinationError && (
                    <Text $theme="error" $variation="secondary" $size="sm">
                      {destinationError}
                    </Text>
                  )}
                </Box>

                {/* Destinations Array  */}
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
                                onClick={() => removeDestination(index)}
                                aria-label={t('Remove destination')}
                                icon={<Icon iconName="delete" />}
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
        </FormProvider>
      ),
      leftAction: (
        <Button color="neutral" variant="secondary" onClick={closeModal}>
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          type="submit"
          form={FORM_ID}
          disabled={
            !methods.formState.isValid ||
            destinations.length === 0 ||
            isSubmitting
          }
        >
          {isSubmitting ? t('Creating...') : t('Create alias')}
        </Button>
      ),
    },
  ];

  return (
    <div id="modal-new-alias">
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
      </CustomModal>
    </div>
  );
};
