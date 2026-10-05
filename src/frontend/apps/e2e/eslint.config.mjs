import { defineConfig } from '@eslint/config-helpers';
import peoplePlugin from 'eslint-plugin-people';

const eslintConfig = defineConfig([
  {
    files: ['**/*.js', '**/*.mjs'],
    plugins: {
      people: peoplePlugin,
    },
    extends: ['people/base'],
    languageOptions: {
      parserOptions: {
        tsconfigRootDir: import.meta.dirname,
        project: ['./tsconfig.json'],
      },
    },
    rules: {
      '@next/next/no-html-link-for-pages': 'off',
    },
  },
]);

export default eslintConfig;
