import Image from 'next/image';

import { Box } from '@/components';

import MailDomainsLogoUrl from '@/features/mail-domains/assets/mail-domains-logo.svg?url';

type MailDomainLogoCircleProps = {
  size?: number;
};

export const MailDomainLogoCircle = ({ size = 24 }: MailDomainLogoCircleProps) => {
  return (
    <Box
      $css={`
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px;
        width: ${size}px;
        height: ${size}px;
        border-radius: 48px;
        border: 1px solid var(--c--contextuals--border--semantic--overlay--primary);
        background: var(--c--contextuals--background--palette--brand--primary);
        position: relative;
      `}
      aria-hidden="true"
    >
      <Image
        alt=""
        src={MailDomainsLogoUrl}
        fill
        style={{ objectFit: 'contain', padding: '3px' }}
        aria-hidden
      />
    </Box>
  );
};
