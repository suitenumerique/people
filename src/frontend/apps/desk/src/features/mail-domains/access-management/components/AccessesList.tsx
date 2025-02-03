import { QuickSearchItemTemplate, UserRow } from '@gouvfr-lasuite/ui-kit';
import { SortModel, usePagination } from '@openfun/cunningham-react';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, SeparatedSection, Text, TextErrors } from '@/components';

import { MailDomain, Role } from '../../domains';
import { useMailDomainAccesses } from '../api';
import { PAGE_SIZE } from '../conf';
import { Access } from '../types';

import { AccessAction } from './AccessAction';

interface AccessesListProps {
  mailDomain: MailDomain;
  currentRole: Role;
}

type SortModelItem = {
  field: string;
  sort: 'asc' | 'desc' | null;
};

const defaultOrderingMapping: Record<string, string> = {
  'user.name': 'user__name',
  'user.email': 'user__email',
  localizedRole: 'role',
};

/**
 * Formats the sorting model based on a given mapping.
 * @param {SortModelItem} sortModel The sorting model item containing field and sort direction.
 * @param {Record<string, string>} mapping The mapping object to map field names.
 * @returns {string} The formatted sorting string.
 * @todo same as team members grid
 */
function formatSortModel(
  sortModel: SortModelItem,
  mapping = defaultOrderingMapping,
) {
  const { field, sort } = sortModel;
  const orderingField = mapping[field] || field;
  return sort === 'desc' ? `-${orderingField}` : orderingField;
}

/**
 * @param mailDomain
 * @param currentRole
 * @todo same as team members grid
 */
export const AccessesList = ({
  mailDomain,
  currentRole,
}: AccessesListProps) => {
  const { t } = useTranslation();
  const pagination = usePagination({
    pageSize: PAGE_SIZE,
  });
  const sortModel: SortModel = [];
  const [accesses, setAccesses] = useState<Access[]>([]);
  const { page, pageSize, setPagesCount } = pagination;

  const ordering = sortModel.length ? formatSortModel(sortModel[0]) : undefined;

  const { data, isLoading, error } = useMailDomainAccesses({
    slug: mailDomain.slug,
    page,
    ordering,
  });

  useEffect(() => {
    if (isLoading) {
      return;
    }

    /*
     * Bug occurs from the Cunningham Datagrid component, when applying sorting
     * on null values. Sanitize empty values to ensure consistent sorting functionality.
     */
    const accesses =
      data?.results?.map((access) => ({
        ...access,
        user: {
          ...access.user,
          full_name: access.user.name,
          name: access.user.name,
          email: access.user.email,
        },
      })) || [];

    setAccesses(accesses);
  }, [data?.results, t, isLoading]);

  useEffect(() => {
    setPagesCount(data?.count ? Math.ceil(data.count / pageSize) : 0);
  }, [data?.count, pageSize, setPagesCount]);

  const localizedRoles = {
    [Role.ADMIN]: t('Administrator'),
    [Role.VIEWER]: t('Viewer'),
    [Role.OWNER]: t('Owner'),
  };

  return (
    <>
      <SeparatedSection />
      <Box
        $margin={{ bottom: 'xl', top: 'md' }}
        $padding={{ horizontal: 'md' }}
      >
        <Text $size="small" $margin={{ bottom: 'md' }} $weight="600">
          {t('Rights shared with ')}
          {accesses.length}
          {t(accesses.length > 1 ? ' peoples' : ' people')}
        </Text>
        {error && <TextErrors causes={error.cause} />}

        {accesses.map((access) => (
          <Box key={access.id} $direction="row" $align="space-between">
            <QuickSearchItemTemplate
              key={access.id}
              left={
                <Box $direction="row" className="c__share-member-item">
                  <UserRow
                    key={access.user.email}
                    fullName={access.user.name}
                    email={access.user.email}
                    showEmail
                  />
                </Box>
              }
            />
            <Box $direction="row" $align="center">
              <Text>{localizedRoles[access.role]}</Text>
              <AccessAction
                mailDomain={mailDomain}
                access={access}
                currentRole={currentRole}
              />
            </Box>
          </Box>
        ))}
      </Box>
    </>
  );
};
