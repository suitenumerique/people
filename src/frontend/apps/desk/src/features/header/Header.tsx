export const HEADER_HEIGHT = '52px';
import Image from 'next/image';

import logoRegieUrl from '@/assets/logo-regie.svg?url';
import { StyledLink } from '@/components/';

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
      <StyledLink href="/" data-testid="header-logo-link">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '1rem',
          }}
        >
          <Image priority src={logoRegieUrl} alt="Régie" height={40} />
        </div>
      </StyledLink>
    </header>
  );
};
