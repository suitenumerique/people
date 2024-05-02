import { create } from 'zustand';

import { EnumMailDomainsOrdering } from '../api/useMailDomains';

interface MailDomainsStore {
  ordering: EnumMailDomainsOrdering;
}

export const useMailDomainsStore = create<MailDomainsStore>(() => ({
  ordering: EnumMailDomainsOrdering.BY_CREATED_AT_DESC,
}));
