# BTA V6.5.4.2 Donations removal

Production status: Pending.

Baseline: `b7e6419322dd37ae9e4d17cb5043f4ad9101516e` (PR #12).
Work package: V6.5.4.2. Candidate and Stage evidence are pending.

This release removes the donation navigation and results entry points, checkout and return pages, four donation API operations, Stripe SDK, and donation-specific implementation and tests. Retired routes return 404. Stay Connected remains available. Account design, store billing, subscriptions, church purchases, HubSpot changes, and V6.5.4.1 language work are outside this release.

The PO confirmed no Stripe payment activity was in progress and approved local completion while resolving Stripe access. Stripe endpoint registration and CRM transfer verification are pending before production promotion. The Stripe account, credentials, and records are retained.

## Local validation

The Next.js static build and 58 frontend tests passed. The exported home and Stay Connected pages served locally and all three retired donation URLs returned 404. Backend regression tests passed (11 passed, 2 skipped, plus 3 subtests). An offline FastAPI probe found no Stripe SDK, verified all four retired APIs return 404, and verified the remaining Stay Connected route forwards consent to a mocked HubSpot integration. The pinned bundle passed checksum, integrity, all 15 edition revisions, and a real local KJV John 3:16 lookup.

## Deployment and rollback

Stage requires separate authorization. Test the exact candidate on protected Vercel and Fly.io Stage, including access controls, normal search, local Scripture retrieval, Stay Connected with fixtures, and retired routes. The pinned SQLite SHA-256 is `edd8495fd4a9db18e28f95665621e964d1fb49992073292aa744b0e148008c0f` with 15 approved editions.

After PO Stage acceptance and production authorization, the PO merges the PR. Verify both provider deployments against the merge SHA. The two services may deploy in either order. A cached donation success page may encounter a retired verification endpoint. Confirm the external webhook disposition before production authorization.

Reconfirm availability of pre-change Vercel deployment `dpl_4PsX6smjGaHX8TkTJK3T7QqJQPuu` and Fly image `deployment-01M84KSG2DAJJJ70MMF0BAV6P2`. Rollback requires separate authorization and compatible runtime configuration. Verify the catalog and real local lookup after rollback.
