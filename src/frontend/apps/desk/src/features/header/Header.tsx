import { Box } from '@/components/';
import { UserInfo } from '@/core/auth/UserInfo';
import { TogglePanelButton } from '@/features/left-panel/components/TogglePanelButton';

import { LaGaufre } from './LaGaufre';
export const HEADER_HEIGHT = '52px';

export const Header = () => {
  return (
    <header
      className=""
      style={{
        display: 'flex',
        position: 'sticky',
        top: '0px',
        left: 0,
        right: 0,
        zIndex: 1000,
        flexDirection: 'row',
        padding: '10px',
        alignItems: 'center',
        justifyContent: 'space-between',
        minHeight: 'var(--header-height)',
        background:
          'linear-gradient(180deg, rgba(255, 255, 255, 0.75) 0%, rgba(255, 255, 255, 0.00) 100%)',
        backdropFilter: 'blur(1px)',
      }}
    >
      <div className="selector-header">
        <TogglePanelButton />
      </div>

      <Box $direction="row">
        <div className="selector-header">
          <UserInfo />
          <LaGaufre />
        </div>
      </Box>
    </header>
  );
};
