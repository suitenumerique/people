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
import { CreateMailboxParams, useCreateMailbox } from '../api';

const FORM_ID = 'form-create-mailbox';

export const ModalCreateMailbox = ({
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

  const createMailboxValidationSchema = z.object({
    first_name: z.string().min(1, t('Please enter your first name')),
    last_name: z.string().min(1, t('Please enter your last name')),
    local_part: z
      .string()
      .regex(/^((?!@|\s)([a-zA-Z0-9.\-]))*$/, t('Invalid format'))
      .min(1, t('You must have minimum 1 character')),
    secondary_email: z.string().email(t('Please enter a valid email address')),
  });

  const methods = useForm<CreateMailboxParams>({
    resolver: zodResolver(createMailboxValidationSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      local_part: '',
      secondary_email: '',
    },
    mode: 'onChange',
  });

  const { mutate: createMailbox, isPending } = useCreateMailbox({
    mailDomainSlug: mailDomain.slug,
    onSuccess: () => {
      toast(t('Mailbox created!'), VariantType.SUCCESS, { duration: 4000 });
      closeModal();
    },
    onError: (error) => {
      toast(t('Mailbox create failed!'), VariantType.ERROR, { duration: 4000 });
      const causes = parseAPIError({ error }) || [];
      setErrorCauses(causes);
    },
  });

  const onSubmitCallback = (event: React.FormEvent) => {
    event.preventDefault();
    void methods.handleSubmit((data) =>
      createMailbox({ ...data, mailDomainSlug: mailDomain.slug }),
    )();
  };

  const steps = [
    {
      title: t('New email account'),
      content: (
        <FormProvider {...methods}>
          {!!errorCauses.length && <TextErrors causes={errorCauses} />}
          <form id={FORM_ID} onSubmit={onSubmitCallback}>
            <Box $padding={{ top: 'sm', horizontal: 'md' }} $gap="4px">
              <Text $size="md" $weight="bold">
                {t('Personal informations')}
              </Text>
              <Text $theme="greyscale" $variation="600">
                {t('Configure the new user.')}
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
                {t('New address')}
              </Text>
            </Box>
            <Box
              $padding="md"
              style={{
                position: 'relative',
                alignItems: 'end',
                gap: '20px',
                flexDirection: 'row',
                alignContent: 'flex-end',
              }}
            >
              <Controller
                name="local_part"
                control={methods.control}
                render={({ field, fieldState }) => (
                  <Box $align="center">
                    <Input
                      {...field}
                      label={t('Name of the new address')}
                      required
                      placeholder={t('firstname.lastname')}
                      error={fieldState.error?.message}
                    />
                  </Box>
                )}
              />
              <Box
                style={{
                  display: 'flex',
                  position: 'absolute',
                  top: '65px',
                  left: '220px',
                }}
              >
                <Text className="mb-8" $weight="500">
                  {' '}
                  @{mailDomain.name}{' '}
                </Text>
              </Box>
            </Box>
          </form>
        </FormProvider>
      ),
      leftAction: (
        <Button color="secondary" onClick={closeModal}>
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          type="submit"
          form={FORM_ID}
          disabled={!methods.formState.isValid || isPending}
        >
          {t('Create')}
        </Button>
      ),
    },
  ];

  return (
    <div id="modal-new-mailbox">
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
        {isPending && (
          <Box $align="center">
            <Loader />
          </Box>
        )}
      </CustomModal>
    </div>
  );
};
