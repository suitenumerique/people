/**
 * Configure Crisp chat for real-time support across all pages.
 */

import { Crisp } from 'crisp-sdk-web';

import { User } from '@/core';

export const initializeCrispSession = (user: User) => {
  if (!Crisp.isCrispInjected()) {
    return;
  }
  Crisp.setTokenId(`people-${user.id}`);
  Crisp.user.setEmail(user.email);
};

export const configureCrispSession = (websiteId: string) => {
  if (Crisp.isCrispInjected()) {
    return;
  }
  Crisp.configure(websiteId);
};

export const terminateSupportSession = () => {
  if (!Crisp.isCrispInjected()) {
    return;
  }
  Crisp.setTokenId();
  Crisp.session.reset();
};