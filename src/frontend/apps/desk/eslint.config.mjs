import { defineConfig } from '@eslint/config-helpers';
import peoplePlugin from 'eslint-plugin-people';

const eslintConfig = defineConfig([
  {
    plugins: {
      docs: peoplePlugin,
    },
    extends: ['people/next'],
    languageOptions: {
      parserOptions: {
        tsconfigRootDir: import.meta.dirname,
        project: ['./tsconfig.json'],
      },
    },
    settings: {
      next: {
        rootDir: import.meta.dirname,
      },
    },
  },
]);

export default eslintConfig;