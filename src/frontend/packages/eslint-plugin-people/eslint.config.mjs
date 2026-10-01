import { defineConfig } from '@eslint/config-helpers';
import peoplePlugins from 'eslint-plugin-people';

const eslintConfig = defineConfig([
  {
    files: ['**/*.js', '**/*.mjs'],
    plugins: {
      docs: peoplePlugins,
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