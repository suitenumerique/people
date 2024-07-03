import { zodResolver } from '@hookform/resolvers/zod';
import {
  Button,
  Input,
  Modal,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import React from 'react';
import {
  Controller,
  FormProvider,
  UseFormReturn,
  useForm,
} from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { Box, Text, TextErrors } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { CreateMailboxParams, useCreateMailbox } from '../../api';
import IconCreateMailbox from '../../assets/create-mailbox.svg';
import { MailDomain } from '../../types';

const FORM_ID: string = 'form-create-mailbox';

const createMailboxValidationSchema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  local_part: z.string().min(1),
  secondary_email: z.string().min(1),
});

export const CreateMailboxForm = ({
  mailDomain,
  setIsFormVisible,
}: {
  mailDomain: MailDomain;
  setIsFormVisible: (value: boolean) => void;
}) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const { colorsTokens } = useCunninghamTheme();

  const methods = useForm<CreateMailboxParams>({
    delayError: 0,
    defaultValues: {
      first_name: '',
      last_name: '',
      local_part: '',
      secondary_email: '',
    },
    mode: 'onChange',
    reValidateMode: 'onChange',
    resolver: zodResolver(createMailboxValidationSchema),
  });

  const { mutate: createMailbox, ...queryState } = useCreateMailbox({
    mailDomainSlug: mailDomain.slug,
    onSuccess: () => {
      toast(t('Mailbox created!'), VariantType.SUCCESS, {
        duration: 4000,
      });

      setIsFormVisible(false);
    },
  });

  const closeModal = () => setIsFormVisible(false);

  const onSubmitCallback = (event: React.FormEvent) => {
    event.preventDefault();
    void methods.handleSubmit((data) =>
      createMailbox({ ...data, mailDomainSlug: mailDomain.slug }),
    )();
  };

  return (
    <FormProvider {...methods}>
      <Modal
        isOpen
        leftActions={
          <Button
            color="secondary"
            fullWidth
            onClick={closeModal}
            disabled={methods.formState.isSubmitting}
          >
            {t('Cancel')}
          </Button>
        }
        onClose={closeModal}
        closeOnClickOutside
        hideCloseButton
        rightActions={
          <Button
            color="primary"
            fullWidth
            type="submit"
            form={FORM_ID}
            disabled={methods.formState.isSubmitting}
          >
            {t('Submit')}
          </Button>
        }
        size={ModalSize.MEDIUM}
        title={
          <Box $align="center" $gap="1rem">
            <IconCreateMailbox
              width={48}
              color={colorsTokens()['primary-text']}
              title={t('Mailbox creation form')}
            />
            <Text $size="h3" $margin="none" role="heading" aria-level={3}>
              {t('Create a mailbox')}
            </Text>
          </Box>
        }
      >
        <Box $width="100%" $margin={{ top: 'large', bottom: 'xl' }}>
          {queryState.isError && (
            <TextErrors className="mb-s" causes={queryState.error.cause} />
          )}
          {methods ? (
            <Form
              methods={methods}
              mailDomain={mailDomain}
              onSubmitCallback={onSubmitCallback}
            />
          ) : null}
        </Box>
      </Modal>
    </FormProvider>
  );
};

const Form = ({
  methods,
  mailDomain,
  onSubmitCallback,
}: {
  methods: UseFormReturn<CreateMailboxParams>;
  mailDomain: MailDomain;
  onSubmitCallback: (event: React.FormEvent) => void;
}) => {
  const { t } = useTranslation();

  return (
    <form onSubmit={onSubmitCallback} id={FORM_ID}>
      <Box $direction="column" $width="100%" $gap="2rem" $margin="auto">
        <Box $margin={{ horizontal: 'none' }}>
          <Controller
            control={methods.control}
            name="first_name"
            render={({ fieldState }) => (
              <Input
                aria-invalid={!!fieldState.error}
                label={t('First name')}
                state={fieldState.error ? 'error' : 'default'}
                text={
                  fieldState.error
                    ? t('Please enter your first name')
                    : undefined
                }
                {...methods.register('first_name')}
              />
            )}
          />
        </Box>

        <Box $margin={{ horizontal: 'none' }}>
          <Controller
            control={methods.control}
            name="last_name"
            render={({ fieldState }) => (
              <Input
                aria-invalid={!!fieldState.error}
                label={t('Last name')}
                state={fieldState.error ? 'error' : 'default'}
                text={
                  fieldState.error
                    ? t('Please enter your last name')
                    : undefined
                }
                {...methods.register('last_name')}
              />
            )}
          />
        </Box>

        <Box $margin={{ horizontal: 'none' }} $direction="row">
          <Box $width="65%">
            <Controller
              control={methods.control}
              name="local_part"
              render={({ fieldState }) => (
                <Input
                  aria-invalid={!!fieldState.error}
                  label={t('Main email address')}
                  state={fieldState.error ? 'error' : 'default'}
                  text={
                    fieldState.error
                      ? t(
                          'Please enter the first part of the email address, without including "@" in it',
                        )
                      : undefined
                  }
                  {...methods.register('local_part')}
                />
              )}
            />
          </Box>

          <Text
            as="span"
            $theme="primary"
            $size="1rem"
            $display="inline-block"
            $css={`
              position: relative; 
              display: inline-block;
              left: 1rem;
              top: 1rem;
            `}
          >
            @{mailDomain.name}
          </Text>
        </Box>

        <Box $margin={{ horizontal: 'none' }}>
          <Controller
            control={methods.control}
            name="secondary_email"
            render={({ fieldState }) => (
              <Input
                aria-invalid={!!fieldState.error}
                label={t('Secondary email address')}
                state={fieldState.error ? 'error' : 'default'}
                text={
                  fieldState.error
                    ? t('Please enter your secondary email address')
                    : undefined
                }
                {...methods.register('secondary_email')}
              />
            )}
          />
        </Box>
      </Box>
    </form>
  );
};
