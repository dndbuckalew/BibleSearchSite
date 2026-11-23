# BTA V6.5.4 Scripture deployment prerequisite

Tracking item `BTA-V6.5.3.x-SCRIPTURE-DEPLOYMENT-01`. Baseline `9619f2c5d5eb7556b32b462ed4aa4585c1c6384e`.

The production Fly build requires the 172,179,456-byte SQLite bundle recovered for V6.5.3. The image carries it at `/app/data/scripture.sqlite` with mode `0444`. Its SHA-256 is `edd8495fd4a9db18e28f95665621e964d1fb49992073292aa744b0e148008c0f`. The build checks SHA-256, SQLite integrity, and all 15 edition IDs and revisions against [the manifest](../../tools/scripture/release-catalog.json). It checks the served catalog and runs John 3:16 through the default KJV query and local retrieval path with networking disabled. The probe closes the stream after the Scripture section, before generation.

## Artifact and deployment

The approved source is the private S3 object `s3://biblical-search-site/bta/scripture/edd8495fd4a9db18e28f95665621e964d1fb49992073292aa744b0e148008c0f/scripture.sqlite` in `us-east-2`. Configure `BTA_SCRIPTURE_ARTIFACT_URI` with that exact object URI and `BTA_SCRIPTURE_ARTIFACT_ROLE_ARN` with an OIDC role granting only `s3:GetObject` on that object. Restrict its trust to audience `sts.amazonaws.com` and subject `repo:dndbuckalew/BibleSearchSite:ref:refs/heads/main`. Keep the bundle and credentials outside Git. Verify the object and role configuration before merge. Verify actual Actions acquisition on the first canonical main workflow run.

From a clean candidate checkout, place the verified recovery file at `data/scripture.sqlite` and run `docker build --platform linux/amd64 -t bta-scripture-candidate .`. To repeat the checks from the resulting image, run `docker run --rm --network none -e OPENAI_API_KEY=offline-verification bta-scripture-candidate python -m tools.scripture.verify_release_bundle`. Expected lookup provenance is source `local`, edition `kjv`, revision `8b330654ade69f7c96268c761da18dc83a1f49b7`.

After PO authorization, deploy the exact approved candidate image to the protected Fly `bta-stage` backend with its existing token gateway and provider-free fixtures supplied as Stage-only machine configuration. Verify the token gateway still denies unauthenticated catalog requests. Record the Stage revision, image digest, in-image artifact checksum, the 15-edition catalog from `/api/scripture/options`, and the local lookup and provenance. For the deployed lookup use the on-machine verifier so it stops before generation. Return the evidence for PO acceptance and production authorization before the PO merges.

A merge to `main` triggers the existing production Fly deployment and the normal Vercel deployment. The frontend source is unchanged. Verify both deploys resolve to the merged revision, then repeat the deployed catalog and local retrieval checks on production. Report a mismatch immediately.

The rollback target is `registry.fly.io/biblesearchsite:deployment-01M81TEWRQTGA27PJDNSS4PY6Z` (digest `sha256:cf7d7c98b00c80ba60d1c2d244e86b757001f11d04769736f11862f5ca3b155b`). Verify availability and obtain separate PO authorization before rolling back. After a rollback, verify the catalog and local lookup again.
