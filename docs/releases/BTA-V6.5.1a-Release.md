# BTA V6.5.1a-Release

Prepared October 27, 2026 for Product Owner review. Donation disablement only; BTA remains free.

## Baseline and preservation

Production repository: https://github.com/dndbuckalew/BibleSearchSite.git (`production` remote).
The workspace `origin` is the separate BibleSearchSite-V6.5 repository.
Live production `main` was verified and fetched at `33b17f642e12c6e84dbc8735a90e470be0d4e158`, merge PR #5, whose release parent is `382700af9d5335dd7c39f3033f6e78e00b6ac648`. Their file trees are identical.
Branch `BTA-V6.5.1a-Release` was created from that production main; the prior `release/v6.5.1` branch was not edited.
No applicable AGENTS.md was found in the repository or its ancestor directories.
The pre-existing generated `frontend/next-env.d.ts` contents were backed up to `%TEMP%/BTA-next-env-preserved.d.ts` and restored byte-for-byte after branch switching and building. This file is ignored on the production baseline.

## Change and entry points

- `frontend/app/platform/capabilities.ts`: single compiled Boolean `DONATIONS_ENABLED = false`; no URL, storage or gesture override.
- `frontend/app/platform/navigation/navigation_configuration.ts`: hides Donate through the shared configuration used by the current disclosure menu and retained desktop/mobile navigation implementations. Filtering removes the complete navigation item.
- `frontend/app/components/donation/ResultsDonationInvitation.tsx`: returns null before its section, spacing, dismiss control and donation link render.
- `frontend/app/donation/page.tsx`: redirects direct donation URLs (including incoming links and query strings) home before rendering donation layout.
- `frontend/app/components/donation/DonationPrompt.tsx`: returns null before rendering any container, children, controls or modal; guards confirmation and checkout handlers before state changes, identifier generation, window opening or requests; disabled effect performs no setup or cleanup registration.
- `frontend/tests/donations-disabled.test.cjs`: focused capability, rendering, route and independently invoked handler tests.

Existing donation layouts, checkout logic and dependencies remain in source. No payment SDK initialization or other payment initiation path was found. The unused DonationPrompt import in `why.tsx` does not mount a component. Backend navigation configuration is not consumed by the current frontend.

`/donation/success` verification/receipt handling and `/donation/cancel` return-home handling remain available for outstanding payments. Backend checkout endpoints and signed webhook processing are unchanged. The frontend flag does not make the public backend checkout endpoint inaccessible. No backend disablement is proposed or implemented.

## Platform and version mapping

Frontend: Next.js 16.1.3 / React 19.2.3, static export. This release covers website donation disablement only. Android wrapper development and validation are a separate workstream already in progress, outside this release scope, and do not block this release. No Android packaging or version metadata changes are included.

Release label `BTA V6.5.1a-Release` maps to branch `BTA-V6.5.1a-Release` and its reviewed patch. The existing private frontend package version remains valid semver `0.1.0`; no repository process requiring a package bump was found. No machine-readable version or build_version.txt change was made.

## Validation

Completed:
- `node --test frontend/tests/*.test.cjs`: 22/22 passing, including existing donation idempotency and TTS reader tests.
- `npm.cmd run build` in frontend: optimized production static export and TypeScript check pass.
- ESLint on all changed application and test files: passes.
- Full lint rerun: 34 errors and 8 warnings, all in unchanged files; fails on existing files (unescaped entities, explicit any, speech-hook ref access and existing CommonJS tests). These files are unchanged; no unrelated lint fixes included.
- Exported home, results, donation and Stay Connected HTML inspected: no donation anchor or dialog; donation export contains the Next redirect instruction to `/` and no donation page content.
- `git diff --check`: passes. Entire backend unchanged against production baseline, including webhook implementation. Stay Connected, scripture-query and TTS/STT implementation files unchanged.

Browser smoke-test attempt and limitations:
- A local static server was started for the existing production export. Browser discovery found Chrome windows but no browser automation connection. Selecting Chrome through computer use failed with `Computer Use app approval timed out`; no page was opened or interacted with. Browser smoke tests are therefore NOT completed.
- Desktop/mobile visual layout, live scripture queries, client navigation/history, static-host direct-link redirection with query strings, request monitoring, live Stay Connected, and TTS/STT audio/permissions remain unverified in a browser. Component rendering tests establish that donation containers and invitations return no markup; they do not establish visual layout on devices.
- Existing reader tests pass and query, navigation, speech and Stay Connected implementations remain unchanged, but this is not a live end-to-end result.
- Production callback/webhook operational validation was not run. Backend and callback source are unchanged.
- Android validation is outside this website release scope and is not a release blocker.

Final diff review against `33b17f6`:
- Exactly seven intended release files: the five frontend implementation/configuration files listed above, the focused test, and this report.
- No backend, dependencies, unrelated application source, package metadata, or production configuration changes.
- `frontend/next-env.d.ts` matches the preserved backup byte-for-byte, is ignored, and is excluded from the release commit.
- Production main was rechecked and remains `33b17f642e12c6e84dbc8735a90e470be0d4e158`.

## Required browser check before merge

Browser smoke testing is REQUIRED before merge and remains outstanding. Exported HTML and component tests do not replace it. The Product Owner may perform this manually and record the tested commit, viewport/browser, results and any failures in PR #6.

PR: https://github.com/dndbuckalew/BibleSearchSite/pull/6

Preview URL from the Vercel bot on PR #6: https://bible-search-site-git-bta-d4e968-donbtadconcepts-5145s-projects.vercel.app

Vercel reported the preview for `c41f0fa` ready. A later documentation commit may trigger an automatic preview refresh; confirm the latest head is Ready in the PR before testing. This is a branch preview, not the production URL. Browser accessibility/authentication and runtime behavior of this URL have not been verified by automation.

Manual checklist (desktop and mobile/narrow viewport):
- Open the preview home page, menu, and results after a Scripture query. Confirm no Donate links/buttons, invitations, donation dialog, empty donation section or orphan spacing appears.
- Open `/donation` and `/donation?donations=true` directly, refresh, and use browser Back/Forward. Confirm return home without donation UI, payment tab or external checkout navigation. With Network Preserve log enabled, confirm no `/donation/create` request during these actions or normal navigation.
- Submit a Scripture question; confirm results render and Home/About/supporting-document navigation works. Record service errors rather than treating them as a pass.
- Exercise relevant Listen/Pause/Resume/Stop and microphone input controls where supported. Record browser permissions, speech support and any untested device/audio behavior.
- Open Stay Connected; verify its form and navigation remain usable. Avoid submitting a real subscription merely for smoke testing; record actual submission as untested if not exercised.
- Record pass/fail for every item in the PR. Do not initiate a real-money transaction. Any browser failures must be resolved or explicitly reviewed before merge approval.

## Production control

The Product Owner authorized committing the seven intended release files, pushing `BTA-V6.5.1a-Release` to the production repository and opening a PR against `main`. No merge, deployment, infrastructure change, Play upload or real-money transaction is authorized or performed. Product Owner approval is required before merge and production rollout. The patch is ready for review, but not cleared for merge: the required browser smoke check above must pass and be recorded before merge approval. Browser smoke-test success is not claimed. PR #6 is already open; its original seven-file release commit was pushed using existing authenticated Git access. Vercel automatically generated a preview from the pushed branch; no manual or production deployment was initiated.

Stripe troubleshooting remains paused. The historical `POST /donation/create` HTTP 503 remains unresolved and has not been investigated or repaired by this release. Secrets, Price configuration, webhook destinations, Fly.io settings, payment persistence, AJT and HCGO architecture remain unchanged.
