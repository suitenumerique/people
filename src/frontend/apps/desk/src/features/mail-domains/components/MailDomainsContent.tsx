import { DataGrid } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';

import { Card } from '@/components';

export function MailDomainsContent() {
  const { t } = useTranslation();

  const dataset = [
    {
      id: '1',
      name: 'John Doe',
      email: 'john@doe.com',
      state: 'Active',
      lastConnection: '2021-09-01',
    },
    {
      id: '2',
      name: 'Jane Doe',
      email: 'jane@doe.com',
      state: 'Inactive',
      lastConnection: '2021-09-02',
    },
  ];

  return (
    <Card $padding="small" $margin="large">
      <DataGrid
        columns={[
          {
            headerName: t('Names'),
            field: 'name',
          },
          {
            field: 'email',
            headerName: t('Emails'),
          },
          {
            field: 'state',
            headerName: t('State'),
          },
          {
            field: 'lastConnection',
            headerName: t('Last Connecttion'),
          },
        ]}
        rows={dataset}
      />
    </Card>
  );
}
