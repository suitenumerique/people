import { zodResolver } from '@hookform/resolvers/zod';
import {
  Button,
  Loader,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import React, { useState } from 'react';
import { Controller, FormProvider, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { APIError } from '@/api/APIError';
import { parseAPIError } from '@/api/parseAPIError';
import {
  Box,
  HorizontalSeparator,
  Input,
  Text,
  TextErrors,
} from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';

import { MailDomain } from '../../domains/types';
import { useUpdateMailbox } from '../api/useUpdateMailbox';
import { ViewMailbox } from '../types';

const FORM_ID = 'form-update-mailbox';

interface ModalUpdateMailboxProps {
  isOpen: boolean;
  onClose: () => void;
  mailDomain: MailDomain;
  mailbox: ViewMailbox;
}

export const ModalUpdateMailbox = ({
  isOpen,
  onClose,
  mailDomain,
  mailbox,
}: ModalUpdateMailboxProps) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const [errorCauses, setErrorCauses] = useState<string[]>([]);
  const [step] = useState(0);

  const updateMailboxValidationSchema = z.object({
    first_name: z.string().min(1, t('Please enter your first name')),
    last_name: z.string().min(1, t('Please enter your last name')),
    secondary_email: z.string().email(t('Please enter a valid email address')),
  });

  const methods = useForm({
    resolver: zodResolver(updateMailboxValidationSchema),
    defaultValues: {
      first_name: mailbox?.first_name || '',
      last_name: mailbox?.last_name || '',
      secondary_email: mailbox?.secondary_email || '',
    },
    mode: 'onChange',
  });

  const { mutate: updateMailbox, isPending } = useUpdateMailbox({
    mailDomainSlug: mailDomain.slug,
    mailboxId: mailbox?.id || '',
    onSuccess: () => {
      toast(t('Mailbox updated!'), VariantType.SUCCESS, { duration: 4000 });
      onClose();
    },
    onError: (error: APIError) => {
      const causes =
        parseAPIError({
          error,
          errorParams: [
            [
              ['Invalid format'],
              t('Invalid format for the email address.'),
              undefined,
            ],
          ],
          serverErrorParams: [
            t(
              'An error occurred while updating the mailbox. Please try again.',
            ),
            undefined,
          ],
        }) || [];
      if (causes.length > 0) {
        causes.forEach((cause) => {
          toast(cause, VariantType.ERROR, { duration: 4000 });
        });
      } else {
        toast(t('Mailbox update failed!'), VariantType.ERROR, {
          duration: 4000,
        });
      }
      setErrorCauses(causes);
    },
  });

  const onSubmitCallback = (event: React.FormEvent) => {
    event.preventDefault();

    if (!mailbox?.id) {
      return;
    }

    void methods.handleSubmit((data) =>
      updateMailbox({ ...data, mailDomainSlug: mailDomain.slug }),
    )();
  };

  if (!mailbox) {
    return null;
  }

  const steps = [
    {
      title: t('Set up account'),
      content: (
        <FormProvider {...methods}>
          {!!errorCauses.length && <TextErrors causes={errorCauses} />}
          <form id={FORM_ID} onSubmit={onSubmitCallback}>
            <Box $padding={{ top: 'sm', horizontal: 'md' }} $gap="4px">
              <Text $size="md" $weight="bold">
                {t('Personal informations')}
              </Text>
              <Text $theme="greyscale" $variation="600">
                {t('Update the user information.')}
              </Text>
            </Box>
            <Box $padding={{ horizontal: 'md' }}>
              <Box $margin={{ top: 'base' }}>
                <Controller
                  name="first_name"
                  control={methods.control}
                  render={({ field, fieldState }) => (
                    <Input
                      {...field}
                      label={t('First name')}
                      placeholder={t('First name')}
                      required
                      error={fieldState.error?.message}
                    />
                  )}
                />
              </Box>
              <Box $margin={{ top: 'base' }}>
                <Controller
                  name="last_name"
                  control={methods.control}
                  render={({ field, fieldState }) => (
                    <Input
                      {...field}
                      label={t('Last name')}
                      placeholder={t('Last name')}
                      required
                      error={fieldState.error?.message}
                    />
                  )}
                />
              </Box>
              <Box $margin={{ top: 'base' }}>
                <Controller
                  name="secondary_email"
                  control={methods.control}
                  render={({ field, fieldState }) => (
                    <Input
                      {...field}
                      label={t('Personal email address')}
                      placeholder={t('john.appleseed@free.fr')}
                      required
                      error={fieldState.error?.message}
                    />
                  )}
                />
                <Text $theme="greyscale" $variation="600">
                  {t(
                    'The person will receive an email at this address to set up their account.',
                  )}
                </Text>
              </Box>
            </Box>

            <HorizontalSeparator $withPadding={true} />

            <Box $padding={{ top: 'base', horizontal: 'md' }}>
              <Text $size="md" $weight="bold">
                {t('Email address')}
              </Text>
            </Box>
            <Box $padding="md">
              <Text>
                {mailbox.local_part}@{mailDomain.name}
              </Text>
            </Box>
          </form>
        </FormProvider>
      ),
      leftAction: (
        <Button color="secondary" onClick={onClose}>
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          type="submit"
          form={FORM_ID}
          disabled={!methods.formState.isValid || isPending}
        >
          {t('Update')}
        </Button>
      ),
    },
  ];

  return (
    <div id="modal-update-mailbox">
      <CustomModal
        isOpen={isOpen}
        hideCloseButton
        step={step}
        totalSteps={steps.length}
        leftActions={steps[step].leftAction}
        rightActions={steps[step].rightAction}
        size={ModalSize.MEDIUM}
        title={steps[step].title}
        onClose={onClose}
        closeOnEsc
        closeOnClickOutside
      >
        {steps[step].content}
        {isPending && (
          <Box $align="center">
            <Loader />
          </Box>
        )}
      </CustomModal>
    </div>
  );
};
