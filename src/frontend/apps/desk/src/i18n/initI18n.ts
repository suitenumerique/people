import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import {
  BASE_LANGUAGE,
  LANGUAGES_ALLOWED,
  LANGUAGE_LOCAL_STORAGE,
} from './conf';
import resources from './translations.json';

i18n
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: BASE_LANGUAGE,
    supportedLngs: Object.keys(LANGUAGES_ALLOWED),
    detection: {
      order: ['cookie', 'navigator'], // detection order
      caches: ['cookie'], // Use cookies to store the language preference
      lookupCookie: LANGUAGE_LOCAL_STORAGE,
      cookieMinutes: 525600, // Expires after one year
    },
    interpolation: {
      escapeValue: false,
    },
    preload: Object.keys(LANGUAGES_ALLOWED),
    nsSeparator: false,
    keySeparator: false,
  })
  .then(() => {
    if (typeof window !== 'undefined') {
      document.documentElement.lang = i18n.language;
    }
  })
  .catch(() => {
    throw new Error('i18n initialization failed');
  });

export default i18n;
