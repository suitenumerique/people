import merge from 'lodash/merge';
import { create } from 'zustand';

import { tokens } from './cunningham-tokens';

type Tokens = typeof tokens.themes.default &
  Partial<(typeof tokens.themes)[keyof typeof tokens.themes]>;
type ColorsTokens = Tokens['globals']['colors'];
type FontSizesTokens = Tokens['globals']['font']['sizes'];
type SpacingsTokens = Tokens['globals']['spacings'];
type ComponentTokens = Partial<
  | (Tokens['components'] & Tokens['globals']['components'])
  | Record<string, unknown>
> &
  Record<string, unknown>;
  
  export const removeQuotes = (str: string) => {
    return str.replace(/^['"]|['"]$/g, "");
  };

export type Theme = keyof typeof tokens.themes;

interface AuthStore {
  theme: string;
  setTheme: (theme: Theme) => void;
  themeTokens: () => Partial<Tokens['globals']>;
  colorsTokens: () => Partial<ColorsTokens>;
  fontSizesTokens: () => Partial<FontSizesTokens>;
  spacingsTokens: () => Partial<SpacingsTokens>;
  componentTokens: () => ComponentTokens;
}

export const useCunninghamTheme = create<AuthStore>((set, get) => {
  const currentTheme = () =>
    merge(
      tokens.themes['default'],
      tokens.themes[get().theme as keyof typeof tokens.themes],
    ) as Tokens;

  return {
    theme: 'dsfr',
    themeTokens: () => currentTheme().globals,
    colorsTokens: () => currentTheme().globals?.colors ?? {},
    componentTokens: () => currentTheme().components,
    spacingsTokens: () => currentTheme().globals?.spacings ?? {},
    fontSizesTokens: () => currentTheme().globals?.font?.sizes ?? {},
    setTheme: (theme: Theme) => {
      set({ theme });
    },
  };
});
