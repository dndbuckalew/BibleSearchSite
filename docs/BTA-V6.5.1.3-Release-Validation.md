# BTA V6.5.1.3 — Performance and Accessibility

Prepared November 17, 2026. Production baseline 5eb243633912c4ea24cefed2d4199349514ad9da. Release remains local pending review and promotion approval.

Changes: remove reader/raw-model diagnostic prints, temporary route markers and credential-prefix output; retain a fixed sanitized selector warning. Initialize expansion before Summary failure handling. Remove the artificial 250ms results-navigation delay and prevent duplicate submission. Add 15-second navigation recovery. Normalize bare English to a regional locale on Windows Edge and improve speech connection-error guidance. Providers, models, prompts, successful response contracts and Scripture content remain unchanged.

Owner-reported stage acceptance: Chrome, genuine Microsoft Edge and Safari inserted dictated text and rendered Scripture. All TTS buttons and Back to Home speech cancellation passed; Chrome playback confirmed on HP and Dell. AVG Secure Browser observations are separate from genuine Edge. Individual confirmation of all four live response sections was not collected; fixture section rendering has automated coverage. Chapter/verse wording clarification remains a separate parsing observation.

Timing samples: stage Genesis query8.78s/results18.94s; stage love query0.143s/results22.60s; production love query0.047s/results27.62s. Production reported cold, stage warm. These are single user observations, not proof of a consistent speedup. Backend results dominates measured waiting; Scripture/AI component times were not separated. Database migration is outside this release.

R2 explicitly deferred by owner to a later focused point release. After the 15-second navigation watchdog unlocks, a prior accepted App Router transition can still commit and replace later editing; retry may repeat provider work. Ordinary navigation speech-cancellation passes do not resolve this risk. No R2 redesign included.

Historical unchanged-candidate evidence reports55 focused tests and frontend build passing, with baseline-equivalent lint findings. Exact isolated release validation is recorded separately before commit. Production Docker uses Python3.11/unpinned requirements whereas stage used pinned Python3.12; runtime equivalence is not claimed. Stage wrappers, certificates, temporary diagnostics and generated builds are excluded.

Rollback: capture current Vercel deployment and Fly image identifiers before merge; restore the captured artifacts if authorized and revert the release merge through reviewed Git history. No force-push/reset. Main merge triggers independent Fly and Vercel production deployments; verify both revisions and production API destination before completion. No production promotion or tag is implied by this record.

## Exact release-tree validation — November 17

Seven backend cleanup tests passed; all55 focused frontend cleanup/STT/TTS tests passed. Default npm run build (Next16.1.3 Turbopack) passed compilation, TypeScript and all14 static pages with production API base https://biblesearchsite.fly.dev. git diff --check passed. Initial dependency-junction build failed due Turbopack filesystem-root restrictions; replacing junction with isolated dependency copy resolved it without application or lockfile edits. No provider query made.

Pre-push gate: production-project branch previews inherit production API settings. Preview isolation must be addressed before branch push; no production setting changed. Current rollback metadata is held in the coordinating promotion package. Local release commit prepared after owner approval; no push/PR/deployment performed at record finalization.
