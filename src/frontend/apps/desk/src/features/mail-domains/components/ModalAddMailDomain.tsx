import { zodResolver } from '@hookform/resolvers/zod';
import {
  Button,
  Input,
  Loader,
  Modal,
  ModalSize,
} from '@openfun/cunningham-react';
import { useRouter } from 'next/navigation';
import React from 'react';
import { Controller, FormProvider, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { Box, StyledLink, Text, TextErrors } from '@/components';
import { useCreateMailDomain } from '@/features/mail-domains';

import { default as MailDomainsLogo } from '../assets/mail-domains-logo.svg';

const FORM_ID = 'form-add-mail-domain';

export const ModalCreateMailDomain = () => {
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

  const onSubmitCallback = () => {
    void methods.handleSubmit(({ name }, event) => {
      event?.preventDefault();
      void createMailDomain(name);
    })();
  };

  const causes = error?.cause?.filter((cause) => {
    const isFound = cause === 'Mail domain with this name already exists.';

    if (isFound) {
      methods.setError('name', {
        type: 'manual',
        message: t(
          'This mail domain is already used. Please, choose another one.',
        ),
      });
    }

    return !isFound;
  });

  if (!methods) {
    return null;
  }

  return (
    <Modal
      isOpen
      leftActions={
        <StyledLink href="/mail-domains">
          <Button color="secondary" tabIndex={-1}>
            {t('Cancel')}
          </Button>
        </StyledLink>
      }
      hideCloseButton
      closeOnClickOutside
      closeOnEsc
      onClose={() => router.push('/mail-domains')}
      rightActions={
        <Button
          onClick={onSubmitCallback}
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
      <FormProvider {...methods}>
        <form action="" id={FORM_ID}>
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
        {!!causes?.length ? <TextErrors causes={causes} /> : null}

        {isPending && (
          <Box $align="center">
            <Loader />
          </Box>
        )}
      </FormProvider>
    </Modal>
  );
};
