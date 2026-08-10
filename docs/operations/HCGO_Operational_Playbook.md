# HCGO Version 6 Implementation Playbook
---

# Purpose
This playbook defines the operational procedures required to execute, validate, and continue HCGO Version 6 implementation.
This document is the operational reference for Version 6.
Implementation prompts shall reference this playbook before beginning development.
This document evolves with the implementation.
---

# Current Version
Version: 6.0
Current Phase:
Current Branch:
Last Updated:
Implementation Status:
## Scope
This playbook documents the operational procedures and commands required to implement and operate HCGO Version 6.
As HCGO evolves, this playbook shall be updated to reflect the current operational workflow, commands, folder structure, and platform architecture.
---

# Quick Command Reference

## Project Root
```powershell
cd "C:\projects\TAD CONCEPTS\Bibical Study Using AI\BibleSearchSite"
```
---

## Git
```powershell
git status
git branch
git fetch origin
git checkout <branch-name>
git pull
git add .
git commit -m "message"
git push
```
---

## Backend
```powershell
cd backend
uvicorn app.main:app --reload
```
---

## Frontend
```powershell
npm run dev
```
---

## PostgreSQL
```powershell
psql -U postgres -d bta_dev
```
```sql
SELECT current_database();
SELECT current_user();
SELECT version();
\dt
\dn
```
---

## SASS
```powershell
python orchestration\sass\run_sass.py
python orchestration\sass\inspection\inspect_source.py
python orchestration\sass\validation\validate_package.py
```
---
## Bootstrap
python orchestration\setup\bootstrap_hcgo.py
'''
---

## HCGO Inventory
```powershell
python tools\hcgo_inventory.py
```
---

## Fly.io
```powershell
fly auth login
fly status
fly ssh console -a biblesearchsite
fly logs
fly secrets list
fly deploy
```
---

## Vercel
```powershell
vercel
vercel login
vercel dev
vercel deploy
vercel --prod
vercel logs
```
---

## Operations
```text
Production URL
https://bibleta.com
Local Frontend
http://localhost:3000
Local Backend
http://127.0.0.1:8000
```

## Pending
```text
SASS Persistence
Knowledge Asset Hub
Translation Publication
```

# Environment

Project Root

```text
C:\projects\TAD CONCEPTS\Bibical Study Using AI\BibleSearchSite
```
---

# Step 0 — Environment Validation

## Purpose
Verify the implementation environment before beginning work.

## Execute
Open VS Code.
Open a new PowerShell terminal.

```powershell
cd "C:\projects\TAD CONCEPTS\Bibical Study Using AI\BibleSearchSite"
```
Verify repository status.

```powershell
git status
```
Verify branch.
```powershell
git branch
```
(Optional)
```powershell
git fetch origin
```

## Expected Result
- Correct implementation branch
- Repository accessible
- Working tree status understood
---

# Step 1 — Backend Startup

## Purpose
Start the HCGO backend.
## Execute
Open a new PowerShell terminal.
```powershell
cd backend
uvicorn app.main:app --reload
```
## Expected Result
Backend starts successfully.
No startup exceptions.
---

# Step 2 — Frontend Startup

## Purpose
Start the Bible TA frontend.
## Execute
Open a second PowerShell terminal.
```powershell
npm run dev
```
## Expected Result
Frontend available at:
```text
http://localhost:3000
```
---

# Step 3 — PostgreSQL Validation

## Purpose
Validate PostgreSQL connectivity.
## Execute
Open a third terminal.
```powershell
psql -U postgres -d bta_dev
```
Execute:
```sql
SELECT current_database();
SELECT current_user();
SELECT version();
```
## Expected Result
Database connection successful.
Database:
```text
bta_dev
```
---

# Step 4 — SASS Operations

## Purpose
Execute the HCGO Source Acquisition Support Service.
---
## Publish Artifact
The human operator reviews the acquired knowledge artifact.
Once approved, the artifact is copied into:
```
text
HCGO Domain/
└── BTA/
    └── 02_approved/
```
Publication of the artifact into `02_approved` constitutes human authorization for SASS processing.
SASS processes only artifacts that have been placed in this location.
---

## Execute Inspection
```powershell
python orchestration\sass\inspection\inspect_source.py
```
Expected
- Artifact discovered
- Inspection completed
- Extraction completed
---

## Execute Validation
```powershell
python orchestration\sass\validation\validate_package.py
```
Expected
Validation completed successfully.
---

## Execute Persistence
(Implementation Pending)
---

## Execute Publication
(Implementation Pending)
---

# Step 5 — Knowledge Asset Hub

## Purpose
Validate publication into the Knowledge Asset Hub.
(Currently Pending)
---
# Validation Checklist
| Component | Status |
|-----------|--------|
| Backend | ☐ |
| Frontend | ☐ |
| PostgreSQL | ☐ |
| SASS Inspection | ☐ |
| SASS Validation | ☐ |
| Persistence | ☐ |
| Knowledge Asset Hub | ☐ |
---
# Current Status
Completed
- Dynamic artifact discovery
- Recursive ZIP discovery
- Hard-coded KJV removal
- Local PostgreSQL connectivity
- Fly.io PostgreSQL connectivity
---
# Next Implementation Task
(To be updated after every completed implementation phase.)
---
# Troubleshooting
Record operational issues encountered during implementation.
Examples
- Backend startup failures
- PostgreSQL connection failures
- Missing Python packages
- Missing Node packages
- Fly.io connectivity issues
---

# Step 5 — HCGO Bootstrap Operations
```powershell
python orchestration\setup\bootstrap_hcgo.py
'''
---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 0.1 | 2026-08-07 | Initial operational playbook |
