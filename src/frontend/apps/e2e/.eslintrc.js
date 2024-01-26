module.exports = {
  root: true,
  extends: ["people/playwright"],
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json"],
  },
  ignorePatterns: ["node_modules"],
};
