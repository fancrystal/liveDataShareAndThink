# Phase 1 Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make current-keyword research, Chinese AI analysis, and downloadable five-page post assets usable end-to-end.

**Architecture:** Add a run-scoped ranking path to the analysis service and return detailed public evidence to DeepSeek. Keep AI validation in provider adapters. Render post-page text into PNG locally in the browser so no image provider is needed.

**Tech Stack:** FastAPI, SQLAlchemy, DeepSeek chat JSON API, React, Canvas API, Vitest, pytest.

---

### Task 1: Run-scoped research

**Files:** `backend/app/collection/service.py`, `backend/app/analysis/service.py`, `backend/app/analysis/router.py`, `backend/tests/analysis/test_vertical_research_api.py`

- [ ] Add a failing test proving a previous project query cannot appear in a new research response.
- [ ] Make collection return a run identifier and let analysis rank only notes whose source query and collection timestamp match the run.
- [ ] Send title, visible content, metrics, collection date, score and URL to the AI report and package request.
- [ ] Run targeted pytest and commit.

### Task 2: Chinese report validation

**Files:** `backend/app/analysis/deepseek_reporter.py`, `backend/tests/analysis/test_deepseek_hot_report.py`

- [ ] Add a failing test with English output followed by compliant Chinese JSON.
- [ ] Validate required strings/lists and reject English letters; retry once with a Chinese correction message.
- [ ] Run targeted pytest and commit.

### Task 3: PNG assets and copy controls

**Files:** `frontend/src/components/PostImageRenderer.ts`, `frontend/src/components/VerticalResearch.tsx`, `frontend/src/styles.css`, `frontend/src/App.test.tsx`

- [ ] Add a failing unit test for five 1080×1440 canvas page descriptors and a component test for copy/download controls.
- [ ] Render five pages with Canvas, expose individual and all-page PNG downloads, and copy caption/tags via Clipboard API.
- [ ] Add loading and success feedback; run Vitest and production build.

### Task 4: End-to-end verification

**Files:** `README.md`

- [ ] Document the research-to-download workflow and its public-data limitations.
- [ ] Run all backend/frontend tests, build Docker images, and call the real DeepSeek-backed API.
- [ ] Commit and push the completed work.
