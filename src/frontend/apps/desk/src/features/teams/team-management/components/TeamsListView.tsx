import { Button, DataGrid } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { Text } from '@/components';
import { TeamsOrdering, useTeams } from '@/features/teams/team-management';

interface TeamsListViewProps {
  querySearch: string;
}

export function TeamsListView({ querySearch }: TeamsListViewProps) {
  const { t } = useTranslation();
  const router = useNavigate();
  const { data, isLoading } = useTeams({
    ordering: TeamsOrdering.BY_CREATED_ON_DESC,
  });
  const teams = React.useMemo(() => data || [], [data]);

  const filteredTeams = React.useMemo(() => {
    if (!querySearch) {
      return teams;
    }
    const lower = querySearch.toLowerCase();
    return teams.filter((team) => team.name.toLowerCase().includes(lower));
  }, [teams, querySearch]);

  return (
    <div role="listbox">
      {filteredTeams && filteredTeams.length ? (
        <DataGrid
          aria-label="listboxTeams"
          rows={filteredTeams}
          columns={[
            {
              field: 'name',
              headerName: t('Team'),
              enableSorting: true,
            },
            {
              id: 'members',
              headerName: t('Member count'),
              enableSorting: false,
              renderCell: ({ row }) => row.accesses.length,
            },
            {
              id: 'actions',
              renderCell: ({ row }) => (
                <Button
                  color="tertiary"
                  onClick={() => router.push(`/teams/${row.id}`)}
                  aria-label={t('View team details')}
                >
                  <span className="material-icons">chevron_right</span>
                </Button>
              ),
            },
          ]}
          isLoading={isLoading}
        />
      ) : null}
      {(!filteredTeams || !filteredTeams.length) && (
        <Text $align="center" $size="small">
          {t('No teams exist.')}
        </Text>
      )}
    </div>
  );
}
