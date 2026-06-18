# Local Development Startup

## Backend

From repository root:

```powershell
uvicorn backend.main:app --reload
```

Expected URL:

```text
http://127.0.0.1:8000
```

---

## Frontend

From repository root:

```powershell
cd frontend
npm run dev
```

Expected URL:

```text
http://localhost:3000
```

---

## Full Local Startup Sequence

1. Open Terminal #1

```powershell
uvicorn backend.main:app --reload
```

2. Open Terminal #2

```powershell
cd frontend
npm run dev
```

3. Open browser

```text
http://localhost:3000
```

4. Verify backend health

```text
http://127.0.0.1:8000
```
# Production

## Public Website

```text
https://www.bibleta.com
```

## Public API

```text
https://www.bibleta.com/api
```

(Adjust if your production API endpoint differs.)

## Production Binding

Application listens on:

```text
0.0.0.0
```

Example:

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

# Environment Summary

| Environment | Frontend | Backend |
|------------|----------|----------|
| Local | http://localhost:3000 | http://127.0.0.1:8000 |
| Production | https://www.bibleta.com | Production API Endpoint |
