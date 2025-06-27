import {
  Button,
  DataGrid,
  Input,
  SortModel,
  usePagination,
} from '@openfun/cunningham-react';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useDebounce } from '@/api';
import IconUser from '@/assets/icons/icon-user.svg';
import { Box, Text, TextErrors } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { ModalAddMembers } from '@/features/teams/member-add';
import { Role, Team } from '@/features/teams/team-management';

import { useTeamAccesses } from '../api';
import IconMagnifyingGlass from '../assets/icon-magnifying-glass.svg';
import { PAGE_SIZE } from '../conf';
import { Access } from '../types';

import { MemberAction } from './MemberAction';

interface MemberGridProps {
  team: Team;
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
 */
function formatSortModel(
  sortModel: SortModelItem,
  mapping: Record<string, string> = defaultOrderingMapping,
): string {
  const { field, sort } = sortModel;
  const orderingField = mapping[field] || field;
  return sort === 'desc' ? `-${orderingField}` : orderingField;
}

export const MemberGrid = ({ team, currentRole }: MemberGridProps) => {
  const [isModalMemberOpen, setIsModalMemberOpen] = useState(false);
  const { t } = useTranslation();
  const [queryValue, setQueryValue] = useState<string>('');
  const { colorsTokens } = useCunninghamTheme();
  const pagination = usePagination({
    pageSize: PAGE_SIZE,
  });

  const [sortModel, setSortModel] = useState<SortModel>([]);
  const [accesses, setAccesses] = useState<Access[]>([]);
  const { page, pageSize, setPagesCount } = pagination;

  const membersQuery = useDebounce(queryValue);
  const ordering = sortModel.length ? formatSortModel(sortModel[0]) : undefined;

  const { data, isLoading, error } = useTeamAccesses({
    teamId: team.id,
    page,
    ordering,
    query: membersQuery,
  });

  useEffect(() => {
    if (isLoading) {
      return;
    }

    const localizedRoles = {
      [Role.ADMIN]: t('Administration'),
      [Role.MEMBER]: t('Member'),
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
          name: access.user.name || '',
          email: access.user.email || '',
        },
      })) || [];

    setAccesses(accesses);
  }, [data?.results, t, isLoading]);

  useEffect(() => {
    setPagesCount(data?.count ? Math.ceil(data.count / pageSize) : 0);
  }, [data?.count, pageSize, setPagesCount]);

  return (
    <div aria-label="Team panel" className="container">
      <Box
        aria-label={t('List members card')}
        $padding={{ all: 'md' }}
        $background="white"
        $justify="space-between"
        $gap="8px"
        $radius="4px"
        $direction="column"
        $css={`
          border: 1px solid ${colorsTokens()['greyscale-200']};
        `}
      >
        <h3 style={{ fontWeight: 700, fontSize: '18px', marginBottom: 'base' }}>
          {t('Group members')}
        </h3>
        <Box
          $direction="row"
          $justify="space-between"
          $align="center"
          $gap="1em"
          $css="width: 100%; margin-bottom: 20px;"
        >
          <Box $css="width: calc(100% - 210px);">
            <Input
              label={t('Filter member list')}
              icon={<IconMagnifyingGlass />}
              value={queryValue}
              onChange={(event) => setQueryValue(event.target.value)}
            />
          </Box>
          <Box
            className="hidden md:flex"
            $css={`
              background: ${colorsTokens()['greyscale-200']};
              height: 32px;
              width: 1px;
            `}
          />
          <Box className="block md:hidden" $css="margin-bottom: 10px;" />
          <Box>
            {currentRole !== Role.MEMBER && (
              <Button
                aria-label={t('Add members to the team')}
                style={{ minWidth: 'auto', maxWidth: 'fit-content' }}
                onClick={() => setIsModalMemberOpen(true)}
              >
                {t('Add a member')}
              </Button>
            )}
          </Box>
        </Box>

        {error && <TextErrors causes={error.cause} />}
        <DataGrid
          columns={[
            {
              headerName: t('Member'),
              id: 'user-info',
              renderCell: ({ row }) => (
                <>
                  <Box $direction="row" $align="center" $gap="1.2em">
                    <IconUser
                      aria-label={t('Member icon')}
                      width={20}
                      height={20}
                      color={colorsTokens()['primary-600']}
                    />
                    <div>
                      <Text
                        $weight="500"
                        $css="text-transform: capitalize;"
                        color={colorsTokens()['greyscale-1000']}
                      >
                        {row.user.name}
                      </Text>
                      <Text
                        $weight="400"
                        color={colorsTokens()['greyscale-600']}
                      >
                        {row.user.email}
                      </Text>
                    </div>
                  </Box>
                </>
              ),
            },
            {
              field: 'localizedRole',
              headerName: t('Roles'),
            },
            {
              id: 'column-actions',
              renderCell: ({ row }) => {
                return (
                  <MemberAction
                    team={team}
                    access={row}
                    currentRole={currentRole}
                  />
                );
              },
            },
          ]}
          aria-label={t('List members card')}
          rows={accesses}
          isLoading={isLoading}
          pagination={pagination}
          onSortModelChange={setSortModel}
          sortModel={sortModel}
        />
      </Box>
      {isModalMemberOpen && (
        <ModalAddMembers
          currentRole={currentRole}
          onClose={() => setIsModalMemberOpen(false)}
          team={team}
        />
      )}
    </div>
  );
};
