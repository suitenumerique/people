import { LanguagePicker as LanguagePickerUi } from '@gouvfr-lasuite/ui-kit';
import { Settings } from 'luxon';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components/';
import { LANGUAGES_ALLOWED } from '@/i18n/conf';

export const LanguagePicker = () => {
  const { i18n } = useTranslation();
  const { preload: languages } = i18n.options;
  Settings.defaultLocale = i18n.language;
  const currentLanguage = Settings.defaultLocale;

  const optionsPicker = useMemo(() => {
    return (languages || []).map((lang) => ({
      value: lang,
      label: LANGUAGES_ALLOWED[lang],
      isChecked: lang === currentLanguage,
      render: () => (
        <Box
          className="c_select__render"
          $direction="row"
          $gap="0.7rem"
          $align="center"
          $css="text-transform: uppercase;"
        >
          <Text $theme="brand" $weight="500" $variation="800">
            {LANGUAGES_ALLOWED[lang]}
          </Text>
        </Box>
      ),
    }));
  }, [languages, currentLanguage]);

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.lang = currentLanguage || i18n.language;
    }
  }, [currentLanguage, i18n.language]);

  return (
    <LanguagePickerUi
      key={currentLanguage}
      languages={optionsPicker}
      size="small"
      onChange={(selected) => {
        type LanguageOption = { value?: string };
        let code: string | undefined;

        if (typeof selected === 'string') {
          code = selected;
        } else if (
          typeof selected === 'object' &&
          selected !== null &&
          typeof (selected as LanguageOption).value === 'string'
        ) {
          code = (selected as LanguageOption).value;
        }

        if (!code) {
          return;
        }

        i18n.changeLanguage(code).catch((err) => {
          console.error('Error changing language', err);
        });
      }}
      compact
    />
  );
};
