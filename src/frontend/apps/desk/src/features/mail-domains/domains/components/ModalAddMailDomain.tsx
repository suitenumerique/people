import { zodResolver } from '@hookform/resolvers/zod';
import { Button, Input, Loader, ModalSize, VariantType } from '@openfun/cunningham-react';
import React, { useState } from 'react';
import { Controller, FormProvider, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { APIError } from '@/api';
import { parseAPIError } from '@/api/parseAPIError';
import { Box, Text, TextErrors } from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';

import { default as MailDomainsLogo } from '../../assets/mail-domains-logo.svg';
import { useAddMailDomain } from '../api';

const FORM_ID = 'form-add-mail-domain';

export const ModalAddMailDomain = ({
  closeModal,
}: {
  closeModal: () => void;
}) => {
  const { t } = useTranslation();

  const [errorCauses, setErrorCauses] = useState<string[]>([]);

  const addMailDomainValidationSchema = z.object({
    name: z.string().min(1, t('Example: saint-laurent.fr')),
    supportEmail: z.string().email(t('Please enter a valid email address')),
  });

  const methods = useForm<{ name: string; supportEmail: string }>({
    delayError: 0,
    defaultValues: {
      name: '',
      supportEmail: '',
    },
    mode: 'onChange',
    reValidateMode: 'onChange',
    resolver: zodResolver(addMailDomainValidationSchema),
  });

  const { mutate: addMailDomain, isPending } = useAddMailDomain({
    onSuccess: () => {
      closeModal();
    },
    onError: (error: APIError) => {
      const unhandledCauses = parseAPIError({
        error,
        errorParams: [
          [
            [
              'Mail domain with this name already exists.',
              'Mail domain with this Slug already exists.',
            ],
            '',
            () => {
              if (methods.formState.errors.name) {
                return;
              }

              methods.setError('name', {
                type: 'manual',
                message: t(
                  'This mail domain is already used. Please, choose another one.',
                ),
              });
              methods.setFocus('name');
            },
          ],
        ],
        serverErrorParams: [
          t(
            'Your request cannot be processed because the server is experiencing an error. If the problem ' +
              'persists, please contact our support to resolve the issue: suiteterritoriale@anct.gouv.fr',
          ),
          () => {
            methods.setFocus('name');
          },
        ],
      });

      setErrorCauses((prevState) =>
        unhandledCauses &&
        JSON.stringify(unhandledCauses) !== JSON.stringify(prevState)
          ? unhandledCauses
          : prevState,
      );
    },
  });


  const onSubmitCallback = (event: React.FormEvent) => {
    event.preventDefault();

    void methods.handleSubmit(({ name, supportEmail }) => {
      void addMailDomain({ name, supportEmail });
    })();
  };

  if (!methods) {
    return null;
  }

    const [step, setStep] = useState(0);

  const steps = [
    {
      title: t('Add a mail domain'),
      content: (
        <Text>{t("You can connect an existing domain name to the DINUM organization. If you don't have a domain name, contact an administrator or read our information document.")}</Text>
      ),
      rightAction: (
        <Button onClick={() => setStep(1)}>
          {t('I have already domain')}
        </Button>
      ),
      leftAction: (
        <Button color="secondary" onClick={closeModal}>
          {t('Close')}
        </Button>
      ),
    },
    {
      title: t('Add a mail domain'),
      content: (
        <>
        {!!errorCauses?.length ? (
        <TextErrors
            $margin={{ bottom: 'large' }}
            $textAlign="left"
            causes={errorCauses}
          />
        ) : null}

        <FormProvider {...methods}>
          <form
            id={FORM_ID}
            onSubmit={onSubmitCallback}
            title={t('Mail domain addition form')}
          >
            <Controller
              control={methods.control}
              name="name"
              render={({ fieldState }) => (
                <Input
                  fullWidth
                  type="text"
                  {...methods.register('name')}
                  aria-invalid={!!fieldState.error}
                  aria-required
                  required
                  autoComplete="off"
                  label={t('Domain name')}
                  state={fieldState.error ? 'error' : 'default'}
                  text={
                    fieldState?.error?.message
                      ? fieldState.error.message
                      : t('Example: saint-laurent.fr')
                  }
                />
              )}
            />
            <Box $margin={{ vertical: '10px' }}>
              <Controller
                control={methods.control}
                name="supportEmail"
                render={({ fieldState }) => (
                  <Input
                    aria-invalid={!!fieldState.error}
                    aria-required
                    required
                    label={t('Support email address')}
                    state={fieldState.error ? 'error' : 'default'}
                    text={
                      fieldState?.error?.message
                        ? fieldState.error.message
                        : t('E.g. : support@example.fr')
                    }
                    {...methods.register('supportEmail')}
                  />
                )}
              />
            </Box>
          </form>

        </FormProvider>
            <Text> {t("Once the domain is added, an administrator will need to validate it. In the meantime, you can still start adding email addresses.")}
            </Text>
        </>
      ),
      leftAction: (
        <Button color="secondary" onClick={() => setStep(0)}>
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          type="submit"
          form={FORM_ID}
          disabled={
            methods.formState.isSubmitting ||
            !methods.formState.isValid ||
            isPending
          }
         >
          {t('Add the domain')}
         </Button>
      )
    },
  ];

  return (
    <CustomModal
      isOpen
      step={step}
      totalSteps={steps.length}
      leftActions={steps[step].leftAction}
      hideCloseButton
      closeOnClickOutside
      onClose={closeModal}
      closeOnEsc
      rightActions={steps[step].rightAction}
      size={ModalSize.MEDIUM}
      title={steps[step].title}
    >
      <Box $padding="md">
        {steps[step].content}
      </Box>
      {isPending && (
        <Box $align="center">
          <Loader />
        </Box>
      )}
    </CustomModal>
  );
};
