# Local Collection Proxy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Docker web UI collect Xiaohongshu public search cards through a protected host-local proxy while retaining a command-line fallback.

**Architecture:** A host companion FastAPI app owns the `xhs-cli` session and returns normalized `PublicSearchCard` data. The main API uses a configurable HTTP gateway in Docker and the existing direct browser gateway locally; existing collection persistence stays unchanged.

**Tech Stack:** FastAPI, httpx, Pydantic Settings, pytest, React, Vitest, Docker Compose.

---

## File Structure

- Create `backend/app/collection/proxy_app.py`: token-protected host-local collection endpoint.
- Create `backend/app/collection/proxy_runner.py`: `uvicorn` module entry point.
- Create `backend/app/collection/xiaohongshu_proxy_gateway.py`: HTTP `SearchGateway` implementation.
- Create `backend/app/collection/gateway_factory.py`: selects proxy/direct gateway.
- Create `backend/tests/collection/test_proxy_app.py`, `test_xiaohongshu_proxy_gateway.py`, `test_gateway_factory.py`.
- Modify `backend/app/core/config.py`, `backend/app/collection/router.py`, `docker-compose.yml`, `.env.example`.
- Modify `frontend/src/components/XiaohongshuImport.tsx`, `frontend/src/App.tsx`, `frontend/src/App.test.tsx`.

### Task 1: Host proxy contract

**Files:** Create proxy app and proxy tests.

- [ ] Write failing tests for a 401 token rejection, blank-keyword 422, and a 200 response delegated to an injected fake `SearchGateway`.
- [ ] Run `pytest backend/tests/collection/test_proxy_app.py -v`; confirm failure because `proxy_app` is absent.
- [ ] Implement `create_proxy_app(gateway, token)` with `POST /api/collections/xiaohongshu/search`, `X-Collection-Proxy-Token`, and `PublicSearchCard` response models. Convert only `XiaohongshuCollectionError` to 422.
- [ ] Re-run the proxy tests; expect pass.
- [ ] Commit `feat: add protected local collection proxy`.

### Task 2: Main API proxy gateway and selection

**Files:** Create HTTP gateway/factory and tests; modify configuration and collection router.

- [ ] Write failing tests showing the HTTP gateway posts keyword and token, converts cards, and produces safe errors for unavailable/401/422 responses; write selection tests for unset/set proxy URL.
- [ ] Run the targeted tests; confirm module-import failure.
- [ ] Implement `XiaohongshuProxyGateway` with injected `httpx.Client`, a 25-second timeout, and safe errors. Add `collection_proxy_url`/`collection_proxy_token` settings; factory returns direct `XiaohongshuBrowserGateway` without a URL and proxy gateway with a URL. Update router dependency to use factory.
- [ ] Re-run targeted tests and `pytest backend/tests -q`; expect pass.
- [ ] Commit `feat: route Docker collection through local proxy`.

### Task 3: Operational configuration and runner

**Files:** Modify compose and env example; create runner.

- [ ] Write a failing runner test asserting `build_proxy_app` uses configured token and the direct browser gateway.
- [ ] Run its test; confirm failure.
- [ ] Add `proxy_runner.py`; add documented blank `COLLECTION_PROXY_TOKEN` in `.env.example`; make Docker API use `COLLECTION_PROXY_URL=http://host.docker.internal:17779` and pass `COLLECTION_PROXY_TOKEN` from its environment without a default secret.
- [ ] Run backend tests and `docker compose -f docker-compose.yml config`; expect no configuration errors.
- [ ] Commit `chore: configure host collection proxy`.

### Task 4: One-click UI feedback and fallback command

**Files:** Modify React import component, app, and test.

- [ ] Write a failing component-level test that starts a deferred import, expects “采集中…”, and verifies a second click cannot start another request.
- [ ] Run `npm test -- --run App.test.tsx`; confirm failure.
- [ ] Add `isCollecting` state via component props, disable controls while pending, and render a short command fallback only for the proxy-unavailable error.
- [ ] Re-run frontend tests and `npm run build`; expect pass.
- [ ] Commit `feat: show local collection proxy progress`.

### Task 5: End-to-end verification and handoff

**Files:** No feature files; optionally update the existing validation note with exact verified commands.

- [ ] Run `pytest backend/tests -q`, `npm test`, and `npm run build`.
- [ ] Run `docker compose -f docker-compose.yml up -d --build`, check API health at `17778`, and check web HTTP 200 at `17777`.
- [ ] Start the host runner with a temporary token, call its health and protected collection route using a fake/injected test path where possible; do not print or persist session secrets.
- [ ] Inspect `git diff --check` and `git status --short`; commit only project files, never `.env`, temporary captures, screenshots, or cookies.

