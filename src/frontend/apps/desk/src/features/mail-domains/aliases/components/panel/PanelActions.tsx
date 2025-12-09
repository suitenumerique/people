import { Box, DropButton, IconOptions, Text } from '@/components';
import { MailDomain } from '@/features/mail-domains/domains';
import { VariantType, useToastProvider } from '@openfun/cunningham-react';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useDeleteAlias } from '../../api';
import { ViewAlias } from '../../types';

export function PanelActions({
  alias,
  mailDomain,
}: {
  alias: ViewAlias;
  mailDomain: MailDomain;
}) {
  const { t } = useTranslation();
  const { toast } = useToastProvider();

  const { mutate: deleteAlias } = useDeleteAlias({
    onSuccess: () => {
      toast(t('Alias deleted successfully'), VariantType.SUCCESS, {
        duration: 4000,
      });
    },
    onError: () => {
      toast(t('Failed to delete alias'), VariantType.ERROR, {
        duration: 4000,
      });
    },
  });

  const handleDelete = () => {
    if (
      window.confirm(
        t('Are you sure you want to delete this alias? This action is irreversible.'),
      )
    ) {
      deleteAlias({
        mailDomainSlug: mailDomain.slug,
        localPart: alias.local_part,
      });
    }
  };

  return (
    <Box $align="center">
      <DropButton
        button={<IconOptions aria-label={t('Display options')} />}
      >
        <Box>
          <button
            onClick={handleDelete}
            style={{
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              padding: '8px 16px',
              width: '100%',
              textAlign: 'left',
            }}
          >
            <Text $theme="danger" $size="small">
              {t('Delete alias')}
            </Text>
          </button>
        </Box>
      </DropButton>
    </Box>
  );
}


