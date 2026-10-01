const { FlatCompat } = require('@eslint/eslintrc');
const js = require('@eslint/js');
const { defineConfig, globalIgnores } = require('eslint/config');

const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

module.exports = defineConfig([
  {
    extends: [...compat.extends('people/next')],

    languageOptions: {
      parserOptions: {
        tsconfigRootDir: __dirname,
        project: ['./tsconfig.json'],
      },
    },

    settings: {
      next: {
        rootDir: __dirname,
      },
    },
  },
  globalIgnores(['**/node_modules', '**/.eslintrc.js']),
]);
