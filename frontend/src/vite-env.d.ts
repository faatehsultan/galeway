/// <reference types="vite/client" />

/* eslint-disable @typescript-eslint/consistent-type-definitions --
   These must be interfaces: they merge with Vite's own declarations (a `type` would be ignored). */
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_SITE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
