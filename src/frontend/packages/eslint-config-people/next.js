const common = require('./common');

module.exports = {
  extends: [
    'people/jest',
    'next',
    'plugin:prettier/recommended',
    'plugin:@tanstack/eslint-plugin-query/recommended',
    'plugin:jsx-a11y/recommended',
  ],
  parserOptions: {
    babelOptions: {
      presets: [require.resolve('next/babel')],
    },
  },
  settings: {
    'jsx-a11y': {
      polymorphicPropName: 'as',
      components: {
        Input: 'input',
        Button: 'button',
        Box: 'div',
        Text: 'span',
        Select: 'select',
      },
    },
  },
  rules: {
    ...common.globalRules,
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'error',
  },
  overrides: common.eslintTS,
  ignorePatterns: ['node_modules'],
};
