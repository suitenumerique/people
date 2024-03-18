import { Button, DataGrid, usePagination } from '@openfun/cunningham-react';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import IconUser from '@/assets/icons/icon-user.svg';
import { Box, Card, TextErrors } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

import { useTeamAccesses } from '../api/useTeamsAccesses';
import { PAGE_SIZE } from '../conf';
import { Role } from '../types';

import { MemberAction } from './MemberAction';
import { ModalAddMembers } from './ModalAddMembers';

interface MemberGridProps {
  teamId: string;
  currentRole: Role;
}

export const MemberGrid = ({ teamId, currentRole }: MemberGridProps) => {
  const [isModalMemberOpen, setIsModalMemberOpen] = useState(false);
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();
  const pagination = usePagination({
    pageSize: PAGE_SIZE,
  });
  const { page, pageSize, setPagesCount } = pagination;
  const { data, isLoading, error } = useTeamAccesses({
    teamId: teamId,
    page,
  });

  const accesses = data?.results;

  useEffect(() => {
    setPagesCount(data?.count ? Math.ceil(data.count / pageSize) : 0);
  }, [data?.count, pageSize, setPagesCount]);

  const dictRole = {
    [Role.ADMIN]: t('Admin'),
    [Role.MEMBER]: t('Member'),
    [Role.OWNER]: t('Owner'),
  };

  return (
    <>
      <Box className="m-b mb-s" $align="flex-end">
        <Button
          aria-label={t('Add members to the team')}
          style={{
            width: 'fit-content',
            minWidth: '8rem',
            justifyContent: 'center',
          }}
          onClick={() => setIsModalMemberOpen(true)}
        >
          {t('Add')}
        </Button>
      </Box>
      <Card
        className="m-b pb-s"
        $overflow="auto"
        $css={`
          margin-top:0;
          & .c__pagination__goto {
            display: none;
          }
          & table th:first-child, 
          & table td:first-child {
            padding-right: 0;
            width: 0;
          }
      `}
        aria-label={t('List members card')}
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
                      aria-label={t('Member icon')}
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
              id: 'role',
              headerName: t('Roles'),
              renderCell({ row }) {
                return dictRole[row.role];
              },
            },
            {
              id: 'column-actions',
              renderCell: ({ row }) => {
                return (
                  <MemberAction
                    teamId={teamId}
                    access={row}
                    currentRole={currentRole}
                  />
                );
              },
            },
          ]}
          rows={accesses || []}
          isLoading={isLoading}
          pagination={pagination}
        />
      </Card>
      {isModalMemberOpen && (
        <ModalAddMembers onClose={() => setIsModalMemberOpen(false)} />
      )}
    </>
  );
};
