# BTA V6.5.1a-Release

Website donation disablement complete based on Product Owner production smoke testing. Donation disablement only; BTA remains free.

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

Preview validation (Product Owner reported, October 27, 2026):
- Desktop preview at commit `943b04c` passed: donation absent from menu and Scripture results; `/donation?donations=true` redirected home; John 3:16 rendered successfully; TTS and STT worked; Stay Connected submission reached HubSpot in approximately 30 seconds.
- These are manual Product Owner results, not automated browser results. Automation previously failed with `Computer Use app approval timed out`.
- Mobile preview validation could not be completed because of phone sign-in access. Mobile is UNVERIFIED, not passed. The Product Owner explicitly accepts proceeding with this limitation.
- Browser/version, desktop viewport, network request monitoring, plain `/donation`, history/refresh combinations, detailed spacing inspection and individual speech transport controls were not separately reported; no additional passes are inferred.
- Exported HTML/component tests supplement manual validation and do not replace browser testing.
- Production callback/webhook operational validation was not run. Backend and callback source are unchanged.
- Android validation remains outside this website release scope and is not a release blocker.

Final diff review against `33b17f6`:
- Exactly seven intended release files: the five frontend implementation/configuration files listed above, the focused test, and this report.
- No backend, dependencies, unrelated application source, package metadata, or production configuration changes.
- `frontend/next-env.d.ts` matches the preserved backup byte-for-byte, is ignored, and is excluded from the release commit.
- At pre-merge review, production main was `33b17f642e12c6e84dbc8735a90e470be0d4e158`; the merged state is recorded below.

## Production validation and release closeout

PR #6: https://github.com/dndbuckalew/BibleSearchSite/pull/6

Repository/API inspection confirms PR #6 is merged into production `main` at merge commit `7849a70a9ae1e4160fc7f04b42510a3c607021af`. Production main was fetched and matches that commit. These facts establish repository merge status; the runtime evidence below is separately reported by the Product Owner.

Product Owner production smoke testing at https://www.bibleta.com:
- Donations are hidden on laptop and phone.
- Laptop Scripture query rendered correctly, with donations absent.
- Phone typed Scripture query rendered correctly.
- Phone microphone query rendered correctly.
- Phone speaker playback successfully read the results.

Observed limitation: an initial phone query using microphone input displayed ?ran into an issue while processing your request. Please try again?. Subsequent typed and microphone queries succeeded. This was a transient observed failure that did not recur during retesting. Its cause was not established; it was not diagnosed or fixed as part of this work.

These are Product Owner manual production results, not agent-run browser checks. Mobile preview testing remains historically unverified because of phone sign-in access; the production phone checks above are distinct subsequent evidence. The preview-only donation query-string redirect, TTS/STT and HubSpot receipt in approximately 30 seconds remain preview evidence and are not represented as separately verified production results. No deployment ID, production test timestamp, browser version, network capture or additional check is inferred.

Release closeout: website donation disablement is complete based on Product Owner production smoke testing, with the transient observed failure recorded above. Android wrapper work remains a separate workstream. Backend webhook operational checks were not performed; webhook source and payment implementation remain preserved.

## Documentation closeout control

This closeout updates only this report and posts the authorized concise validation comment to merged PR #6. Documentation changes are submitted from a separate branch through a PR against production `main`, with no direct main commit. No application code, payment configuration, secrets or infrastructure changes are included. No new production deployment is initiated, and the documentation PR is not merged by the agent. The existing ignored local `frontend/next-env.d.ts` is excluded.

Stripe troubleshooting remains paused. The historical `POST /donation/create` HTTP 503 remains unresolved and has not been investigated or repaired by this release. Secrets, Price configuration, webhook destinations, Fly.io settings, payment persistence, AJT and HCGO architecture remain unchanged.
