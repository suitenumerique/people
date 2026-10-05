import { defineConfig } from '@eslint/config-helpers';
import peoplePlugin from 'eslint-plugin-people';

const eslintConfig = defineConfig([
  {
    files: ['**/*.js', '**/*.mjs'],
    plugins: {
      people: peoplePlugin,
    },
    extends: ['people/next', 'people/test'],
    languageOptions: {
      parserOptions: {
        tsconfigRootDir: import.meta.dirname,
        project: ['./tsconfig.json'],
      },
    },
  },
]);

export default eslintConfig;
