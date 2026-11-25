import js from "@eslint/js";
import pluginQuery from "@tanstack/eslint-plugin-query";
import importX from "eslint-plugin-import-x";
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "dist",
      "coverage",
      "node_modules",
      "src/routeTree.gen.ts",
      "src/lib/api/schema.d.ts",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  jsxA11y.flatConfigs.strict,
  ...pluginQuery.configs["flat/recommended"],
  reactHooks.configs.flat.recommended,
  {
    languageOptions: {
      globals: { ...globals.browser },
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    plugins: { "import-x": importX },
    rules: {
      "import-x/order": ["error", { "newlines-between": "always", alphabetize: { order: "asc" } }],
      "import-x/no-default-export": "error",
      "@typescript-eslint/consistent-type-definitions": ["error", "type"],
      "@typescript-eslint/no-non-null-assertion": "error",
      "no-console": "error",
    },
  },
  {
    // Tooling config files are plain JS outside the type-aware project.
    files: ["*.config.{js,ts}"],
    ...tseslint.configs.disableTypeChecked,
  },
  {
    // Config files must default-export.
    files: ["*.config.{js,ts}"],
    rules: { "import-x/no-default-export": "off" },
  },
  {
    files: ["src/**/*.test.{ts,tsx}", "src/test/**", "build/**/*.test.ts"],
    rules: { "@typescript-eslint/no-non-null-assertion": "off" },
  },
);
