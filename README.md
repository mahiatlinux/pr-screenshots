# PR 11273 verification

The base banner gives a terminal command. At head, the banner and Settings explain that an already-running Studio server prevents an update, then instruct the user to stop that server and quit and reopen the desktop app.

Separate production builds use the same component fixture, package lock and browser inputs. The browser assertion requires the banner to match the locale message on head and merge, and to differ on base. External-server Update remains disabled and Settings has no install button. Owned-server automatic and manual-package actions each invoke both component callbacks. Text and buttons fit at both viewport widths in all 12 locales.

These are component browser checks with synthetic ownership/update state. They do not execute a native installer.

Commands run in each isolated frontend:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run typecheck
npm run i18n:check:strict
node --experimental-strip-types --test tests/tauri-update-schedule.test.ts tests/update-banner-flex-priority.test.ts
node_modules/.bin/vite build --config review-vite.config.ts
```

The fixture files and Playwright assertions are included. Original screenshots are preserved beside the labelled composites. Blank space is trimmed in composites without scaling the components.

Chromium 145.0.7632.6 and Firefox 146.0.1 each passed 78 browser scenarios. WebKit could not launch because its Ubuntu 24.04 fallback build requires libraries absent on this Ubuntu 26.04 host.
