import { DataGrid, SortModel, usePagination } from '@openfun/cunningham-react';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import IconUser from '@/assets/icons/icon-user.svg';
import { Box, Card, TextErrors } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { MailDomain, Role } from '../../domains';
import { useMailDomainAccesses } from '../api';
import { PAGE_SIZE } from '../conf';
import { Access } from '../types';

import { AccessAction } from './AccessAction';

interface AccessesGridProps {
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
export const AccessesGrid = ({
  mailDomain,
  currentRole,
}: AccessesGridProps) => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();
  const pagination = usePagination({
    pageSize: PAGE_SIZE,
  });
  const [sortModel, setSortModel] = useState<SortModel>([]);
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

    const localizedRoles = {
      [Role.ADMIN]: t('Administrator'),
      [Role.VIEWER]: t('Viewer'),
      [Role.OWNER]: t('Owner'),
    };

    /*
     * Bug occurs from the Cunningham Datagrid component, when applying sorting
     * on null values. Sanitize empty values to ensure consistent sorting functionality.
     */
    const accesses =
      data?.results?.map((access) => ({
        ...access,
        localizedRole: localizedRoles[access.role],
        user: {
          ...access.user,
          name: access.user.name,
          email: access.user.email,
        },
      })) || [];

    setAccesses(accesses);
  }, [data?.results, t, isLoading]);

  useEffect(() => {
    setPagesCount(data?.count ? Math.ceil(data.count / pageSize) : 0);
  }, [data?.count, pageSize, setPagesCount]);

  return (
    <Card
      $padding={{ bottom: 'small' }}
      $margin={{ all: 'big', top: 'none' }}
      $overflow="auto"
      $css={`
          & .c__pagination__goto {
            display: none;
          }
          & table th:first-child, 
          & table td:first-child {
            padding-right: 0;
            width: 3.5rem;
          }
          & table td:last-child {
            text-align: right;
          }
      `}
      aria-label={t('Accesses list card')}
    >
      {error && <TextErrors causes={error.cause} />}

      <DataGrid
        columns={[
          {
            id: 'icon-user',
            renderCell() {
              return (
                <Box $direction="row" $align="center">
                  <IconUser
                    aria-label={t('Access icon')}
                    width={20}
                    height={20}
                    color={colorsTokens()['primary-600']}
                  />
                </Box>
              );
            },
          },
          {
            headerName: t('Names'),
            field: 'user.name',
          },
          {
            field: 'user.email',
            headerName: t('Emails'),
          },
          {
            field: 'localizedRole',
            headerName: t('Roles'),
          },
          {
            id: 'column-actions',
            renderCell: ({ row }) => (
              <AccessAction
                mailDomain={mailDomain}
                access={row}
                currentRole={currentRole}
              />
            ),
          },
        ]}
        rows={accesses}
        isLoading={isLoading}
        pagination={pagination}
        onSortModelChange={setSortModel}
        sortModel={sortModel}
      />
    </Card>
  );
};
