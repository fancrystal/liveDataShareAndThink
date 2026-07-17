# Phase 1 Closeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the single-user Xiaohongshu content-attraction workflow with DeepSeek fallback, evidence-based insights, project/history access, and transparent proxy state.

**Architecture:** The API keeps collection and persistence boundaries unchanged. A generation decorator handles DeepSeek failure, deterministic analysis creates traceable pattern insights, and lightweight read endpoints feed the existing React workbench.

**Tech Stack:** FastAPI, SQLAlchemy, httpx, Pydantic, React, Vitest, pytest, Docker Compose.

---

### Task 1: DeepSeek-first fallback

**Files:** Create `backend/app/generation/fallback_adapter.py`; modify `factory.py`, `docker-compose.yml`; test `backend/tests/generation/test_generation_factory.py`.

- [ ] Write failing tests for DeepSeek selection with a template fallback and template-only selection.
- [ ] Run `python -m pytest backend/tests/generation/test_generation_factory.py -v`; confirm missing fallback behavior.
- [ ] Implement `FallbackGenerator(primary, fallback)` that catches only `DeepSeekGenerationError`, add generator name `deepseek:...->template`, and pass all DeepSeek environment values through Docker Compose.
- [ ] Re-run targeted generation tests; expect pass.

### Task 2: Content-attraction pattern insight

**Files:** Create `backend/app/analysis/patterns.py`; modify `analysis/service.py`, `analysis/schemas.py`, `analysis/router.py`; test `backend/tests/analysis/test_content_patterns.py`.

- [ ] Write a failing test that supplies collected titles/content/types and expects hook labels, format counts, three angles, and source note IDs.
- [ ] Run the targeted test; confirm module or response-field failure.
- [ ] Implement deterministic sentence/title extraction and attach a second persisted insight with its own evidence rows; expose it from ranking response.
- [ ] Re-run analysis tests; expect pass.

### Task 3: Collection history and proxy state

**Files:** Modify collection schemas/service/router and proxy app; create `backend/tests/collection/test_collection_history.py`, `test_proxy_status.py`.

- [ ] Write failing API tests for reverse-chronological collection history and token-safe proxy state/health responses.
- [ ] Run targeted tests; confirm routes are absent.
- [ ] Add run read schema, service query, collection history route, proxy health route, and main API configuration-only proxy-status route.
- [ ] Re-run targeted tests; expect pass.

### Task 4: Project re-entry and closeout UI

**Files:** Modify `frontend/src/api/*`, `App.tsx`, `NotesPreview.tsx`; create `ProjectPicker.tsx`, `CollectionHistory.tsx`, `ContentAttractionInsight.tsx`; modify `App.test.tsx`.

- [ ] Write failing UI tests for opening an existing project, showing a collection run, and rendering the attraction insight.
- [ ] Run `npm.cmd test -- --run src/App.test.tsx`; confirm components/API methods are absent.
- [ ] Implement read API methods and focused components; render generator/proxy labels and “未公开” for absent public fields.
- [ ] Re-run frontend tests and build; expect pass.

### Task 5: Verification and handoff

**Files:** Modify `README.md` only if it exists and lacks the new startup/configuration steps.

- [ ] Run backend tests, frontend tests, frontend build, Docker Compose config, and `git diff --check`.
- [ ] Verify Docker API health and the web HTTP response after rebuild when configuration permits.
- [ ] Commit only source, tests, Compose, and docs; exclude `.env`, browser sessions, temporary captures, and showcase files.

