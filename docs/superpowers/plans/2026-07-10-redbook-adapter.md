# Redbook Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe, testable, read-only `redbook` keyword-import path without exposing browser credentials to the application.

**Architecture:** A `RedbookAdapter` implements the current collection port and receives a command runner for deterministic tests. The collection service remains the sole writer of normalized notes and metric snapshots. A dedicated route instantiates the adapter and maps adapter errors to safe client messages.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, pytest, Python standard-library subprocess.

---

### Task 1: Define and test the adapter boundary

**Files:**
- Create: `backend/app/collection/redbook_adapter.py`
- Create: `backend/tests/collection/test_redbook_adapter.py`
- Modify: `backend/app/collection/ports.py`

- [ ] **Step 1: Write failing adapter tests**

```python
def test_search_notes_normalizes_redbook_json():
    adapter = RedbookAdapter(runner=lambda args: '{"notes": []}')
    assert adapter.search_notes("护肤").source == "redbook"

def test_search_notes_explains_missing_cli():
    adapter = RedbookAdapter(runner=raise_file_not_found)
    with pytest.raises(RedbookAdapterError, match="redbook"):
        adapter.search_notes("护肤")
```

- [ ] **Step 2: Run adapter tests and verify they fail**

Run: `python -m pytest backend/tests/collection/test_redbook_adapter.py -v`  
Expected: import failure because `redbook_adapter` does not exist.

- [ ] **Step 3: Implement the minimal adapter**

Implement a runner accepting `list[str]`, invoke `redbook search <keyword> --sort popular --json`, parse JSON, normalize fields into `FixturePayload`, and raise a redacted `RedbookAdapterError` for missing command, non-zero exit, invalid JSON, or incomplete items.

- [ ] **Step 4: Run adapter tests and verify they pass**

Run: `python -m pytest backend/tests/collection/test_redbook_adapter.py -v`  
Expected: PASS.

### Task 2: Expose keyword import through the API

**Files:**
- Modify: `backend/app/collection/router.py`
- Modify: `backend/tests/collection/test_fixture_import.py`

- [ ] **Step 1: Write the failing API test**

```python
def test_redbook_import_uses_collection_service(client, project, monkeypatch):
    monkeypatch.setattr(router, "RedbookAdapter", FakeRedbookAdapter)
    response = client.post(f"/api/projects/{project['id']}/collections/redbook?keyword=护肤")
    assert response.status_code == 201
    assert response.json()["notes_created"] == 1
```

- [ ] **Step 2: Run the API test and verify it fails**

Run: `python -m pytest backend/tests/collection/test_fixture_import.py -v`  
Expected: route missing.

- [ ] **Step 3: Implement the route and error mapping**

Add `POST /api/projects/{project_id}/collections/redbook`, require a nonblank keyword, use `CollectionService(session, RedbookAdapter())`, and translate `RedbookAdapterError` to HTTP 422.

- [ ] **Step 4: Run collection tests and verify they pass**

Run: `python -m pytest backend/tests/collection -v`  
Expected: PASS.

### Task 3: Document local preparation and verify the application

**Files:**
- Modify: `README.md`
- Modify: `docs/research/xiaohongshu-login-crawling-analysis.md`

- [ ] **Step 1: Document the manual setup**

Document Node.js 22+, `npm install -g @lucasygu/redbook`, Chrome login, `redbook whoami`, the read-only route, and that no Cookie is stored by the application.

- [ ] **Step 2: Run regression checks**

Run: `python -m pytest backend/tests -v`  
Expected: all backend tests pass.

- [ ] **Step 3: Commit**

```powershell
git add backend README.md docs
git commit -m "feat: import Xiaohongshu keyword samples through redbook"
```
