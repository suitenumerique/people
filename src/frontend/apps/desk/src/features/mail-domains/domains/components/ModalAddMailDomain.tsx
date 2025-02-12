import { zodResolver } from '@hookform/resolvers/zod';
import { Button, Input, Loader, ModalSize } from '@openfun/cunningham-react';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { Controller, FormProvider, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { APIError } from '@/api';
import { parseAPIError } from '@/api/parseAPIError';
import { Box, Text, TextErrors } from '@/components';
import { Modal } from '@/components/Modal';

import { default as MailDomainsLogo } from '../../assets/mail-domains-logo.svg';
import { useAddMailDomain } from '../api';

const FORM_ID = 'form-add-mail-domain';

export const ModalAddMailDomain = () => {
  const { t } = useTranslation();
  const router = useRouter();

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
    onSuccess: (mailDomain) => {
      router.push(`/mail-domains/${mailDomain.slug}`);
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

  return (
    <Modal
      isOpen
      leftActions={
        <Button color="secondary" onClick={() => router.push('/mail-domains/')}>
          {t('Cancel')}
        </Button>
      }
      hideCloseButton
      closeOnClickOutside
      closeOnEsc
      onClose={() => router.push('/mail-domains/')}
      rightActions={
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
      }
      size={ModalSize.MEDIUM}
      title={
        <>
          <MailDomainsLogo aria-hidden="true" />
          <Text as="h3" $textAlign="center">
            {t('Add a mail domain')}
          </Text>
        </>
      }
    >
      {!!errorCauses?.length ? (
        <TextErrors
          $margin={{ bottom: 'small' }}
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

        {isPending && (
          <Box $align="center">
            <Loader />
          </Box>
        )}
      </FormProvider>
    </Modal>
  );
};
