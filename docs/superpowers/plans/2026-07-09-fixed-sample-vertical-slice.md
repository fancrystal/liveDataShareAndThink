# Fixed-Sample Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first locally deployable vertical slice that turns a research project and fixed Xiaohongshu samples into explainable rankings and three reviewable content drafts.

**Architecture:** Use a modular FastAPI application with synchronous SQLAlchemy repositories, PostgreSQL in Docker, and SQLite for isolated tests. A React/Vite single-page workbench calls the API. Platform and AI boundaries are protocols; this milestone implements fixture adapters so core behavior is testable without Xiaohongshu login or an external model.

**Tech Stack:** Python 3.13, FastAPI 0.139, SQLAlchemy 2.0, Pydantic 2, PostgreSQL 17, pytest, React 19, TypeScript, Vite 8, Vitest, Docker Compose.

---

## Scope

This plan implements milestone one from the approved design:

- project and brand-profile creation;
- fixed Xiaohongshu sample import;
- notes and metric snapshots persisted with provenance;
- explainable relative-performance ranking;
- evidence-backed topic creation;
- deterministic generation of three draft variants;
- review approval and structured export;
- a minimal Web workbench for the complete flow.

It deliberately excludes real Xiaohongshu login, `redbook`, Redis workers, external LLMs, automatic publishing, multi-user accounts, and live-stream analysis. Those receive separate plans after this slice is green.

## File Map

```text
.
├── .env.example                         # Local configuration contract
├── .gitignore                           # Python, Node, secrets, generated data
├── compose.yaml                         # PostgreSQL, backend, frontend
├── README.md                            # Local setup and verification
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── app/
│   │   ├── main.py                      # FastAPI composition root
│   │   ├── core/config.py               # Environment settings
│   │   ├── db/base.py                   # Declarative base and model imports
│   │   ├── db/session.py                # Engine and session dependency
│   │   ├── projects/models.py           # Project and BrandProfile ORM
│   │   ├── projects/schemas.py          # Project API contracts
│   │   ├── projects/service.py          # Project use cases
│   │   ├── projects/router.py           # Project HTTP endpoints
│   │   ├── collection/models.py         # Note, MetricSnapshot, CollectionRun
│   │   ├── collection/schemas.py        # Collection API contracts
│   │   ├── collection/ports.py          # Platform-adapter protocol
│   │   ├── collection/fixture_adapter.py# JSON fixture implementation
│   │   ├── collection/service.py        # Import and deduplication
│   │   ├── collection/router.py         # Import and sample endpoints
│   │   ├── analysis/models.py           # Insight and Evidence ORM
│   │   ├── analysis/scoring.py          # Pure explainable scoring
│   │   ├── analysis/schemas.py          # Ranking API contracts
│   │   ├── analysis/service.py          # Ranking and evidence persistence
│   │   ├── analysis/router.py           # Analysis endpoints
│   │   ├── generation/models.py         # TopicIdea, Draft, DraftVersion, Review
│   │   ├── generation/schemas.py        # Generation and review contracts
│   │   ├── generation/ports.py          # Generator protocol
│   │   ├── generation/template_adapter.py # Deterministic generator
│   │   ├── generation/service.py        # Topic, generation, review, export
│   │   └── generation/router.py         # Generation endpoints
│   └── tests/
│       ├── conftest.py                  # SQLite app fixture
│       ├── fixtures/xhs_notes.json      # Stable Xiaohongshu-like sample
│       ├── test_health.py
│       ├── projects/test_projects_api.py
│       ├── collection/test_fixture_import.py
│       ├── analysis/test_scoring.py
│       ├── analysis/test_analysis_api.py
│       └── generation/test_generation_flow.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/client.ts
        ├── api/types.ts
        ├── components/ProjectForm.tsx
        ├── components/SampleImport.tsx
        ├── components/RankingTable.tsx
        ├── components/DraftWorkbench.tsx
        ├── styles.css
        └── App.test.tsx
```

### Task 1: Repository and FastAPI Foundation

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Test: `backend/tests/test_health.py`

- [ ] **Step 1: Write the failing health test**

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_service_status() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "live-data-share-and-think",
        "phase": "content-growth",
    }
```

- [ ] **Step 2: Install backend dependencies and prove the test fails**

Run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest backend\tests\test_health.py -v
```

Expected: collection fails because `app.main` does not exist.

- [ ] **Step 3: Add configuration and the minimal application**

`backend/app/core/config.py`:

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "live-data-share-and-think"
    database_url: str = "sqlite:///./local.db"
    fixture_path: str = "backend/tests/fixtures/xhs_notes.json"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`backend/app/main.py`:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="LiveDataShareAndThink")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "live-data-share-and-think",
            "phase": "content-growth",
        }

    return app


app = create_app()
```

- [ ] **Step 4: Run the health test**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests\test_health.py -v`

Expected: `1 passed`.

- [ ] **Step 5: Commit the foundation**

```powershell
git add .gitignore .env.example backend
git commit -m "build: add FastAPI foundation"
```

### Task 2: Project and Brand Profile Persistence

**Files:**
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/projects/__init__.py`
- Create: `backend/app/projects/models.py`
- Create: `backend/app/projects/schemas.py`
- Create: `backend/app/projects/service.py`
- Create: `backend/app/projects/router.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/conftest.py`
- Test: `backend/tests/projects/test_projects_api.py`

- [ ] **Step 1: Write the failing project API test**

```python
def test_create_and_read_project(client):
    created = client.post(
        "/api/projects",
        json={
            "name": "护肤直播增长",
            "description": "研究敏感肌直播引流",
            "brand_profile": {
                "name": "小鹿护肤",
                "positioning": "成分透明的敏感肌护肤",
                "target_audience": "25-35岁敏感肌女性",
                "tone": "专业、克制、友好",
                "core_value": "降低试错成本",
                "forbidden_terms": ["根治", "百分百有效"],
            },
        },
    )

    assert created.status_code == 201
    project_id = created.json()["id"]
    fetched = client.get(f"/api/projects/{project_id}")
    assert fetched.status_code == 200
    assert fetched.json()["brand_profile"]["positioning"] == "成分透明的敏感肌护肤"
```

- [ ] **Step 2: Run it and verify the route is missing**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests\projects\test_projects_api.py -v`

Expected: `404 Not Found`.

- [ ] **Step 3: Implement the ORM, schemas, service, and router**

Use UUID string primary keys and a one-to-one `BrandProfile`. `ProjectService` receives a SQLAlchemy `Session` and exposes `create(payload: ProjectCreate) -> Project`, `get(project_id: str) -> Project`, and `list() -> list[Project]`.

Required endpoints:

```text
POST /api/projects       -> 201 ProjectRead
GET  /api/projects       -> 200 list[ProjectRead]
GET  /api/projects/{id}  -> 200 ProjectRead or 404
```

`backend/app/db/session.py` exposes `build_engine(database_url: str) -> Engine`, `build_session_factory(engine: Engine) -> sessionmaker[Session]`, and the FastAPI dependency `get_session() -> Iterator[Session]`.

`create_app()` accepts an optional session dependency override so tests use an isolated SQLite database.

- [ ] **Step 4: Run project and health tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests\test_health.py backend\tests\projects -v`

Expected: all tests pass.

- [ ] **Step 5: Commit project persistence**

```powershell
git add backend/app/db backend/app/projects backend/app/main.py backend/tests
git commit -m "feat: add research projects"
```

### Task 3: Fixed-Sample Collection Adapter

**Files:**
- Create: `backend/app/collection/__init__.py`
- Create: `backend/app/collection/models.py`
- Create: `backend/app/collection/schemas.py`
- Create: `backend/app/collection/ports.py`
- Create: `backend/app/collection/fixture_adapter.py`
- Create: `backend/app/collection/service.py`
- Create: `backend/app/collection/router.py`
- Create: `backend/tests/fixtures/xhs_notes.json`
- Modify: `backend/app/db/base.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/collection/test_fixture_import.py`

- [ ] **Step 1: Create a three-note fixture with provenance**

The JSON fixture contains three notes under keyword `敏感肌`:

```json
{
  "source": "fixture",
  "query": "敏感肌",
  "collected_at": "2026-07-09T10:00:00+08:00",
  "notes": [
    {
      "platform_note_id": "fixture-note-1",
      "url": "https://www.xiaohongshu.com/explore/fixture-note-1",
      "author": {"platform_author_id": "author-1", "nickname": "阿宁护肤", "followers": 1200},
      "title": "敏感肌别再盲买了",
      "content": "先看屏障状态，再选清洁和保湿。",
      "content_type": "image",
      "published_at": "2026-07-08T10:00:00+08:00",
      "metrics": {"likes": 860, "favorites": 620, "comments": 143, "shares": 31}
    },
    {
      "platform_note_id": "fixture-note-2",
      "url": "https://www.xiaohongshu.com/explore/fixture-note-2",
      "author": {"platform_author_id": "author-2", "nickname": "成分小周", "followers": 25000},
      "title": "夏天修护清单",
      "content": "三个步骤建立日常修护流程。",
      "content_type": "image",
      "published_at": "2026-07-05T12:00:00+08:00",
      "metrics": {"likes": 1900, "favorites": 1100, "comments": 96, "shares": 42}
    },
    {
      "platform_note_id": "fixture-note-3",
      "url": "https://www.xiaohongshu.com/explore/fixture-note-3",
      "author": {"platform_author_id": "author-3", "nickname": "真实试用员", "followers": 600},
      "title": "泛红时我只做这两件事",
      "content": "停止叠加产品，记录刺激来源。",
      "content_type": "video",
      "published_at": "2026-07-09T08:00:00+08:00",
      "metrics": {"likes": 420, "favorites": 180, "comments": 88, "shares": 15}
    }
  ]
}
```

- [ ] **Step 2: Write the failing import and idempotency test**

```python
def test_fixture_import_is_idempotent(client, project):
    first = client.post(f"/api/projects/{project['id']}/collections/fixture")
    second = client.post(f"/api/projects/{project['id']}/collections/fixture")

    assert first.status_code == 201
    assert first.json()["notes_created"] == 3
    assert second.status_code == 201
    assert second.json()["notes_created"] == 0
    assert second.json()["metric_snapshots_created"] == 3

    notes = client.get(f"/api/projects/{project['id']}/notes").json()
    assert len(notes) == 3
    assert all(note["source"]["adapter"] == "fixture" for note in notes)
```

- [ ] **Step 3: Run it and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests\collection\test_fixture_import.py -v`

Expected: collection route is missing.

- [ ] **Step 4: Implement the adapter contract and import service**

`ports.py`:

```python
from typing import Protocol


class PlatformAdapter(Protocol):
    @property
    def name(self) -> str:
        raise NotImplementedError

    def search_notes(self, keyword: str) -> list["CollectedNote"]:
        raise NotImplementedError
```

`CollectionService.import_keyword()` must:

1. create a `CollectionRun`;
2. upsert authors and notes by platform ID;
3. always append a new metric snapshot;
4. keep source adapter, query, collection time, and raw JSON;
5. mark the run `succeeded`;
6. return created and updated counts.

Required endpoints:

```text
POST /api/projects/{id}/collections/fixture -> 201 CollectionSummary
GET  /api/projects/{id}/notes               -> 200 list[NoteRead]
```

- [ ] **Step 5: Run all backend tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests -v`

Expected: all tests pass.

- [ ] **Step 6: Commit fixture collection**

```powershell
git add backend/app/collection backend/app/db/base.py backend/app/main.py backend/tests
git commit -m "feat: import fixed Xiaohongshu samples"
```

### Task 4: Explainable Relative-Performance Analysis

**Files:**
- Create: `backend/app/analysis/__init__.py`
- Create: `backend/app/analysis/models.py`
- Create: `backend/app/analysis/scoring.py`
- Create: `backend/app/analysis/schemas.py`
- Create: `backend/app/analysis/service.py`
- Create: `backend/app/analysis/router.py`
- Modify: `backend/app/db/base.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/analysis/test_scoring.py`
- Test: `backend/tests/analysis/test_analysis_api.py`

- [ ] **Step 1: Write pure scoring tests**

```python
from app.analysis.scoring import MetricInput, score_note


def test_small_author_outperformance_is_visible():
    score = score_note(
        MetricInput(likes=860, favorites=620, comments=143, shares=31, followers=1200, age_hours=24),
        cohort_median_engagement=600,
    )

    assert 0 <= score.total <= 100
    assert score.author_efficiency > 80
    assert score.confidence == "high"
    assert score.explanation["followers"] == 1200


def test_missing_followers_reduce_confidence_without_becoming_zero():
    score = score_note(
        MetricInput(likes=50, favorites=20, comments=5, shares=None, followers=None, age_hours=12),
        cohort_median_engagement=80,
    )

    assert score.author_efficiency is None
    assert score.confidence == "medium"
```

- [ ] **Step 2: Run them and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests\analysis\test_scoring.py -v`

Expected: `app.analysis.scoring` is missing.

- [ ] **Step 3: Implement deterministic scoring**

Expose:

```python
@dataclass(frozen=True)
class MetricInput:
    likes: int | None
    favorites: int | None
    comments: int | None
    shares: int | None
    followers: int | None
    age_hours: float


@dataclass(frozen=True)
class NoteScore:
    total: float
    engagement: float
    velocity: float
    cohort_relative: float
    author_efficiency: float | None
    confidence: Literal["low", "medium", "high"]
    explanation: dict[str, int | float | None]


def score_note(metrics: MetricInput, cohort_median_engagement: float) -> NoteScore:
    """Return version-one explainable score using the rules below."""
    raise NotImplementedError
```

Rules:

- weighted engagement is `likes + 1.5*favorites + 2*comments + 2*shares`;
- each component uses `log1p` before normalization;
- velocity divides weighted engagement by `max(age_hours, 1)`;
- cohort score compares weighted engagement to the cohort median;
- author efficiency compares engagement with `max(followers, 1)`;
- missing fields are excluded, never converted to observed zero;
- confidence is high with all fields and at least three notes, medium with one missing dimension, otherwise low;
- total weights are engagement 35%, velocity 25%, cohort 25%, author efficiency 15%; redistribute the author weight when followers are unknown.

- [ ] **Step 4: Write the failing analysis API test**

```python
def test_analysis_returns_ranked_notes_with_evidence(client, imported_project):
    response = client.post(f"/api/projects/{imported_project['id']}/analysis/rank")

    assert response.status_code == 201
    payload = response.json()
    assert len(payload["rankings"]) == 3
    assert payload["rankings"][0]["score"]["total"] >= payload["rankings"][1]["score"]["total"]
    assert payload["insight"]["confidence"] in {"medium", "high"}
    assert len(payload["insight"]["evidence"]) == 3
```

- [ ] **Step 5: Implement ranking and persisted evidence**

The analysis service reads each note's latest snapshot, calculates the cohort median, persists one `Insight(type="relative_performance")`, and creates one `Evidence` row per ranked note with the metric-snapshot ID and score contribution.

Required endpoint:

```text
POST /api/projects/{id}/analysis/rank -> 201 RankingReport
```

- [ ] **Step 6: Run scoring, API, and full backend tests**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests -v`

Expected: all tests pass.

- [ ] **Step 7: Commit explainable analysis**

```powershell
git add backend/app/analysis backend/app/db/base.py backend/app/main.py backend/tests
git commit -m "feat: rank content with evidence"
```

### Task 5: Topic, Draft, Review, and Export Flow

**Files:**
- Create: `backend/app/generation/__init__.py`
- Create: `backend/app/generation/models.py`
- Create: `backend/app/generation/schemas.py`
- Create: `backend/app/generation/ports.py`
- Create: `backend/app/generation/template_adapter.py`
- Create: `backend/app/generation/service.py`
- Create: `backend/app/generation/router.py`
- Modify: `backend/app/db/base.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/generation/test_generation_flow.py`

- [ ] **Step 1: Write the failing complete generation-flow test**

```python
def test_topic_generates_three_reviewable_versions(client, analyzed_project):
    topic = client.post(
        f"/api/projects/{analyzed_project['id']}/topics",
        json={
            "title": "敏感肌直播前先做减法",
            "target_audience": "反复泛红且频繁换产品的人",
            "content_goal": "live_preview",
            "angle": "用两步自查降低试错",
            "insight_id": analyzed_project["insight_id"],
        },
    ).json()

    generated = client.post(f"/api/topics/{topic['id']}/drafts/generate")
    assert generated.status_code == 201
    drafts = generated.json()
    assert len(drafts) == 3
    assert {draft["variant"] for draft in drafts} == {"practical", "story", "contrarian"}
    assert all(draft["evidence_ids"] for draft in drafts)

    version_id = drafts[0]["current_version"]["id"]
    approved = client.post(f"/api/draft-versions/{version_id}/reviews", json={"decision": "approved", "note": "可用"})
    assert approved.status_code == 201

    exported = client.get(f"/api/draft-versions/{version_id}/export")
    assert exported.status_code == 200
    assert exported.json()["status"] == "approved"
```

- [ ] **Step 2: Run it and verify failure**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests\generation\test_generation_flow.py -v`

Expected: topic route is missing.

- [ ] **Step 3: Define the generator protocol**

```python
@dataclass(frozen=True)
class GenerationBrief:
    topic: str
    audience: str
    goal: Literal["live_preview", "live_booking", "post_live_followup"]
    angle: str
    brand_tone: str
    forbidden_terms: Sequence[str]
    evidence_summaries: Sequence[str]


@dataclass(frozen=True)
class GeneratedContent:
    variant: Literal["practical", "story", "contrarian"]
    title: str
    body: str
    tags: Sequence[str]
    cover_text: str


class ContentGenerator(Protocol):
    @property
    def name(self) -> str:
        raise NotImplementedError

    def generate(self, brief: GenerationBrief) -> list[GeneratedContent]:
        raise NotImplementedError
```

- [ ] **Step 4: Implement the deterministic template adapter and validation**

The adapter returns exactly three variants. Validation rejects:

- empty title or body;
- title longer than the configured Xiaohongshu limit;
- any forbidden term;
- duplicate titles;
- a draft with no evidence IDs.

Each successful generation creates three `Draft` rows and one immutable `DraftVersion` per draft. Store generator name `fixture-template-v1` and the input brief as JSON.

- [ ] **Step 5: Implement review and export**

Allowed review decisions are `returned` and `approved`. Export returns 409 unless the version has an approved review. Export JSON contains title, body, tags, cover text, evidence IDs, version number, and status.

Required endpoints:

```text
POST /api/projects/{id}/topics                   -> 201 TopicRead
POST /api/topics/{id}/drafts/generate            -> 201 list[DraftRead]
POST /api/draft-versions/{id}/reviews            -> 201 ReviewRead
GET  /api/draft-versions/{id}/export             -> 200 ExportRead or 409
```

- [ ] **Step 6: Run the complete backend suite**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests -v`

Expected: all tests pass.

- [ ] **Step 7: Commit generation workflow**

```powershell
git add backend/app/generation backend/app/db/base.py backend/app/main.py backend/tests
git commit -m "feat: generate and review evidence-backed drafts"
```

### Task 6: React Workbench

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/types.ts`
- Create: `frontend/src/components/ProjectForm.tsx`
- Create: `frontend/src/components/SampleImport.tsx`
- Create: `frontend/src/components/RankingTable.tsx`
- Create: `frontend/src/components/DraftWorkbench.tsx`
- Create: `frontend/src/styles.css`
- Test: `frontend/src/App.test.tsx`

- [ ] **Step 1: Create the frontend package and install dependencies**

`package.json` scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

Install React, React DOM, Vite, TypeScript, Vitest, jsdom, Testing Library, and the Vite React plugin using `npm.cmd`.

- [ ] **Step 2: Write the failing workbench test**

```tsx
it("runs the fixed-sample workflow", async () => {
  render(<App api={fakeApi} />);

  await userEvent.type(screen.getByLabelText("项目名称"), "护肤直播增长");
  await userEvent.click(screen.getByRole("button", { name: "创建项目" }));
  await userEvent.click(screen.getByRole("button", { name: "导入固定样本" }));
  await userEvent.click(screen.getByRole("button", { name: "运行分析" }));

  expect(await screen.findByText("敏感肌别再盲买了")).toBeInTheDocument();
  expect(screen.getByText(/置信度/)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "生成三个草稿" })).toBeEnabled();
});
```

- [ ] **Step 3: Run it and verify failure**

Run: `npm.cmd --prefix frontend test`

Expected: test fails because `App` and its workflow do not exist.

- [ ] **Step 4: Implement the single-page workbench**

The page displays:

- project and brand-profile form;
- current workflow step;
- fixed-sample import summary;
- ranked notes with total, sub-scores, confidence, and evidence;
- topic form populated from the leading insight;
- three draft cards;
- review and export actions.

The API client methods are:

```typescript
createProject(input: ProjectCreate): Promise<Project>
importFixture(projectId: string): Promise<CollectionSummary>
rankNotes(projectId: string): Promise<RankingReport>
createTopic(projectId: string, input: TopicCreate): Promise<Topic>
generateDrafts(topicId: string): Promise<Draft[]>
reviewDraftVersion(versionId: string, decision: ReviewDecision): Promise<Review>
exportDraftVersion(versionId: string): Promise<DraftExport>
```

- [ ] **Step 5: Run tests and production build**

Run:

```powershell
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
```

Expected: tests pass and Vite produces `frontend/dist`.

- [ ] **Step 6: Commit the workbench**

```powershell
git add frontend
git commit -m "feat: add content research workbench"
```

### Task 7: Containers, End-to-End Verification, and Documentation

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `compose.yaml`
- Create: `README.md`
- Create: `backend/tests/test_vertical_slice.py`
- Modify: `.env.example`

- [ ] **Step 1: Write the failing API vertical-slice test**

The test performs the complete approved flow through HTTP:

```python
def test_fixed_sample_vertical_slice(client):
    project = create_project(client)
    assert client.post(f"/api/projects/{project['id']}/collections/fixture").status_code == 201
    report = client.post(f"/api/projects/{project['id']}/analysis/rank").json()
    topic = create_topic(client, project["id"], report["insight"]["id"])
    drafts = client.post(f"/api/topics/{topic['id']}/drafts/generate").json()
    version_id = drafts[0]["current_version"]["id"]
    assert client.get(f"/api/draft-versions/{version_id}/export").status_code == 409
    assert client.post(
        f"/api/draft-versions/{version_id}/reviews",
        json={"decision": "approved", "note": "final"},
    ).status_code == 201
    assert client.get(f"/api/draft-versions/{version_id}/export").status_code == 200
```

- [ ] **Step 2: Run it and confirm any missing integration fails**

Run: `.\.venv\Scripts\python.exe -m pytest backend\tests\test_vertical_slice.py -v`

Expected: failure identifies any missing route composition or transaction boundary.

- [ ] **Step 3: Add production containers**

`compose.yaml` defines:

- `db`: PostgreSQL 17 with a named volume and health check;
- `api`: backend on port 8000, waiting for healthy database;
- `web`: frontend on port 5173, configured with `VITE_API_URL=http://localhost:8000/api`.

Do not place real credentials in Compose. Read them from `.env`.

- [ ] **Step 4: Document setup and checks**

README commands:

```powershell
Copy-Item .env.example .env
docker compose up --build
.\.venv\Scripts\python.exe -m pytest backend\tests -v
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
```

Document that this milestone uses fixtures and that real Xiaohongshu login is the next plan.

- [ ] **Step 5: Run all verification**

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -v
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
docker compose config
```

Expected: all tests pass, frontend builds, and Compose configuration validates.

- [ ] **Step 6: Commit the deployable vertical slice**

```powershell
git add .env.example .gitignore README.md compose.yaml backend frontend
git commit -m "feat: complete fixed-sample vertical slice"
```

## Completion Checkpoint

The milestone is complete only when:

- the backend test suite passes;
- the frontend test suite passes;
- the production frontend build succeeds;
- `docker compose config` succeeds;
- `git status --short` is clean;
- the fixed-sample flow creates three notes, an explainable ranking, one evidence-backed topic, three draft variants, an approval, and an export;
- no secret, Cookie, generated database, virtual environment, or `node_modules` file is tracked.
