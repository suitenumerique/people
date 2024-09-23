import { create } from 'zustand';

import { EnumMailDomainsOrdering } from '@/features/mail-domains/domains/api';

interface MailDomainsStore {
  ordering: EnumMailDomainsOrdering;
  changeOrdering: () => void;
}

export const useMailDomainsStore = create<MailDomainsStore>((set) => ({
  ordering: EnumMailDomainsOrdering.BY_CREATED_AT_DESC,
  changeOrdering: () =>
    set(({ ordering }) => ({
      ordering:
        ordering === EnumMailDomainsOrdering.BY_CREATED_AT
          ? EnumMailDomainsOrdering.BY_CREATED_AT_DESC
          : EnumMailDomainsOrdering.BY_CREATED_AT,
    })),
}));
