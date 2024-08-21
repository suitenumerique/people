import { zodResolver } from '@hookform/resolvers/zod';
import { Button, Input, Loader, ModalSize } from '@openfun/cunningham-react';
import { useRouter } from 'next/navigation';
import React from 'react';
import {
  Controller,
  FormProvider,
  UseFormReturn,
  useForm,
} from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { APIError } from '@/api';
import { Box, Text, TextErrors } from '@/components';
import { Modal } from '@/components/Modal';
import { useCreateMailDomain } from '@/features/mail-domains';

import { default as MailDomainsLogo } from '../assets/mail-domains-logo.svg';

const FORM_ID = 'form-add-mail-domain';

const useAddMailDomainApiError = ({
  error,
  methods,
}: {
  error: APIError | null;
  methods: UseFormReturn<{ name: string }> | null;
}): string[] | undefined => {
  const [errorCauses, setErrorCauses] = React.useState<undefined | string[]>(
    undefined,
  );
  const { t } = useTranslation();

  React.useEffect(() => {
    if (methods && t && error) {
      let causes = undefined;

      if (error.cause?.length) {
        const parseCauses = (causes: string[]) =>
          causes.reduce((arrayCauses, cause) => {
            switch (cause) {
              case 'Mail domain with this name already exists.':
              case 'Mail domain with this Slug already exists.':
                methods.setError('name', {
                  type: 'manual',
                  message: t(
                    'This mail domain is already used. Please, choose another one.',
                  ),
                });
                break;
              default:
                arrayCauses.push(cause);
            }

            return arrayCauses;
          }, [] as string[]);

        causes = parseCauses(error.cause);
      }

      if (error.status === 500 || !error.cause) {
        causes = [
          t(
            'Your request cannot be processed because the server is experiencing an error. If the problem ' +
              'persists, please contact our support to resolve the issue: suiteterritoriale@anct.gouv.fr.',
          ),
        ];
      }

      setErrorCauses(causes);
    }
  }, [methods, t, error]);

  React.useEffect(() => {
    if (errorCauses && methods) {
      methods.setFocus('name');
    }
  }, [methods, errorCauses]);

  return errorCauses;
};

export const ModalAddMailDomain = () => {
  const { t } = useTranslation();
  const router = useRouter();

  const createMailDomainValidationSchema = z.object({
    name: z.string().min(1, t('Example: saint-laurent.fr')),
  });

  const methods = useForm<{ name: string }>({
    delayError: 0,
    defaultValues: {
      name: '',
    },
    mode: 'onChange',
    reValidateMode: 'onChange',
    resolver: zodResolver(createMailDomainValidationSchema),
  });

  const {
    mutate: createMailDomain,
    isPending,
    error,
  } = useCreateMailDomain({
    onSuccess: (mailDomain) => {
      router.push(`/mail-domains/${mailDomain.slug}`);
    },
  });

  const errorCauses = useAddMailDomainApiError({ error, methods });

  const onSubmitCallback = (event: React.FormEvent) => {
    event.preventDefault();

    void methods.handleSubmit(({ name }) => {
      void createMailDomain(name);
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
          disabled={!methods.watch('name') || isPending}
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
        <form id={FORM_ID} onSubmit={onSubmitCallback}>
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
