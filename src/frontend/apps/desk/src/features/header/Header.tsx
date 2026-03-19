import Image from 'next/image';

import { default as IconRegie } from '@/assets/logo-regie.svg?url';
import { StyledLink } from '@/components/';
import { UserInfo } from '@/core/auth/UserInfo';
import { useLeftPanelStore } from '@/features/left-panel';
import { TogglePanelButton } from '@/features/left-panel/components/TogglePanelButton';

import { LaGaufre } from './LaGaufre';
export const HEADER_HEIGHT = '52px';

export const Header = () => {
  const { isPanelOpen } = useLeftPanelStore();

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
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          borderRadius: '8px',
          backgroundColor:
            'var(--c--contextuals--background--surface--primary)',
          backdropFilter: 'blur(10px)',
          border: '1px solid var(--c--contextuals--border--surface--primary)',
          padding: '4px',
          flexDirection: 'row',
          boxShadow: '0 2px 4px 0 rgba(0, 0, 0, 0.05)',
        }}
      >
        <TogglePanelButton />
        <div
          style={{
            overflow: 'hidden',
            maxWidth: isPanelOpen ? '0' : '120px',
            opacity: isPanelOpen ? '0' : '1',
            transition: 'max-width 0.3s ease, opacity 0.2s ease 0.3s',
          }}
        >
          <StyledLink href="/">
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <Image priority src={IconRegie} alt="Régie Logo" height={34} />
            </div>
          </StyledLink>
        </div>
      </div>

      <div className="">
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            borderRadius: '8px',
            backgroundColor:
              'var(--c--contextuals--background--surface--primary)',
            border: '1px solid var(--c--contextuals--border--surface--primary)',
            padding: '4px',
            gap: '4px',
            flexDirection: 'row',
            boxShadow: '0 2px 4px 0 rgba(0, 0, 0, 0.05)',
          }}
        >
          <UserInfo />
          <LaGaufre />
        </div>
      </div>
    </header>
  );
};
