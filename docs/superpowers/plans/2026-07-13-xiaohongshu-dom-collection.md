# Xiaohongshu DOM Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Let one local user import public Xiaohongshu keyword-search cards through their existing local login and run the current Phase 1 ranking and draft workflow on those notes.

**Architecture:** A \`XiaohongshuDomAdapter\` implements the existing collection port. A local Camoufox gateway reads the previously saved \`xhs-cli\` session only in memory, extracts a bounded public-card DTO list from the search DOM, and the existing \`CollectionService\` remains the sole database writer. React adds an explicit keyword import panel plus a bounded note preview.

**Tech Stack:** Python 3.13, FastAPI, Pydantic, SQLAlchemy, Camoufox/Playwright through \`xhs-cli\`, pytest, React, TypeScript, Vitest.

---

## File structure

- \`backend/app/collection/xiaohongshu_dom_adapter.py\`: card DTO, count normalization, and \`PlatformAdapter\` implementation.
- \`backend/app/collection/xiaohongshu_browser_gateway.py\`: local session loading, bounded page DOM extraction, and redacted errors.
- \`backend/app/collection/router.py\`: adapter factory and public import route.
- \`backend/tests/collection/test_xiaohongshu_dom_adapter.py\`: pure adapter/gateway tests.
- \`backend/tests/collection/test_fixture_import.py\`: successful and safe-error route tests.
- \`frontend/src/components/XiaohongshuImport.tsx\`: keyword and collection controls.
- \`frontend/src/components/NotesPreview.tsx\`: imported-note preview.
- \`frontend/src/api/types.ts\`, \`frontend/src/api/client.ts\`, \`frontend/src/App.tsx\`: API contract and flow wiring.
- \`frontend/src/App.test.tsx\`: browser-visible Phase 1 flow.
- \`backend/requirements.txt\`, \`README.md\`, \`.gitignore\`: setup and local-artifact safety.

### Task 1: Normalize public search cards without a browser

**Files:**
- Create: \`backend/app/collection/xiaohongshu_dom_adapter.py\`
- Create: \`backend/tests/collection/test_xiaohongshu_dom_adapter.py\`

- [ ] **Step 1: Write the failing desired-behavior test**

\`\`\`python
from datetime import UTC, datetime

from app.collection.xiaohongshu_dom_adapter import PublicSearchCard, XiaohongshuDomAdapter


class FakeGateway:
    def search(self, keyword: str) -> list[PublicSearchCard]:
        return [PublicSearchCard(
            note_id="note-1", url="https://www.xiaohongshu.com/explore/note-1",
            title="敏感肌护肤步骤", content="先做减法", author_id="author-1",
            author_name="小鹿", content_type="image", published_at="2026-07-10T08:00:00Z",
            likes="1.2万", favorites="300", comments="8", shares=None,
        )]


def test_search_notes_normalizes_visible_public_card() -> None:
    adapter = XiaohongshuDomAdapter(FakeGateway(), clock=lambda: datetime(2026, 7, 13, tzinfo=UTC))
    result = adapter.search_notes(" 敏感肌 ")
    assert result.source == "xiaohongshu-dom"
    assert result.query == "敏感肌"
    assert result.notes[0].metrics.likes == 12_000
    assert result.notes[0].metrics.shares is None
\`\`\`

- [ ] **Step 2: Run the test and confirm RED**

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/collection/test_xiaohongshu_dom_adapter.py -v\`  
Expected: FAIL because the adapter module is absent.

- [ ] **Step 3: Implement the smallest adapter**

\`\`\`python
@dataclass(frozen=True)
class PublicSearchCard:
    note_id: str
    url: str
    title: str
    content: str
    author_id: str
    author_name: str
    content_type: str
    published_at: str
    likes: str | None = None
    favorites: str | None = None
    comments: str | None = None
    shares: str | None = None


class XiaohongshuDomAdapter:
    name = "xiaohongshu-dom"

    def __init__(self, gateway: SearchGateway, clock: Callable[[], datetime] = lambda: datetime.now(UTC)) -> None:
        self.gateway, self.clock = gateway, clock

    def search_notes(self, keyword: str) -> FixturePayload:
        query = keyword.strip()
        if not query:
            raise XiaohongshuCollectionError("请输入非空关键词后再采集。")
        cards = self.gateway.search(query)
        if not cards:
            raise XiaohongshuCollectionError("没有发现可导入的公开搜索结果，请换一个关键词后重试。")
        return FixturePayload(source=self.name, query=query, collected_at=self.clock(), notes=[self._note(card) for card in cards])
\`\`\`

Implement \`_note\` with existing \`CollectedNote\`, \`CollectedAuthor\`, and \`CollectedMetrics\`. Implement \`parse_visible_count\`: \`"1.2万"\` becomes \`12000\`; decimal/plain strings become integers; absent or unparseable values are \`None\`.

- [ ] **Step 4: Run GREEN**

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/collection/test_xiaohongshu_dom_adapter.py -v\`  
Expected: PASS.

- [ ] **Step 5: Add red tests for blank keyword and unknown counts**

\`\`\`python
import pytest


def test_search_notes_rejects_blank_keyword() -> None:
    with pytest.raises(XiaohongshuCollectionError, match="非空关键词"):
        XiaohongshuDomAdapter(FakeGateway()).search_notes("   ")


def test_parse_visible_count_returns_none_for_unknown_text() -> None:
    assert parse_visible_count("热度很高") is None
\`\`\`

- [ ] **Step 6: Run RED, implement only validation/count parsing, then run GREEN**

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/collection/test_xiaohongshu_dom_adapter.py -v\`  
Expected: new tests first FAIL, then all PASS.

- [ ] **Step 7: Commit**

\`\`\`powershell
git add backend/app/collection/xiaohongshu_dom_adapter.py backend/tests/collection/test_xiaohongshu_dom_adapter.py
git commit -m "feat: normalize Xiaohongshu public search cards"
\`\`\`

### Task 2: Load the existing local session and extract page cards

**Files:**
- Create: \`backend/app/collection/xiaohongshu_browser_gateway.py\`
- Modify: \`backend/requirements.txt\`
- Modify: \`backend/tests/collection/test_xiaohongshu_dom_adapter.py\`

- [ ] **Step 1: Write a failing gateway unit test with a fake page**

\`\`\`python
from app.collection.xiaohongshu_browser_gateway import XiaohongshuBrowserGateway


class FakePage:
    def __init__(self, cards: list[dict[str, str | None]]) -> None:
        self.cards = cards

    def evaluate(self, _script: str) -> list[dict[str, str | None]]:
        return self.cards


def test_extract_cards_returns_public_fields_only() -> None:
    page = FakePage([{
        "note_id": "note-1", "url": "https://www.xiaohongshu.com/explore/note-1",
        "title": "敏感肌护肤步骤", "content": "先做减法", "author_id": "author-1",
        "author_name": "小鹿", "content_type": "image", "published_at": "",
        "likes": "1.2万", "favorites": "300", "comments": "8", "shares": None,
    }])
    cards = XiaohongshuBrowserGateway.extract_cards(page)
    assert cards[0].note_id == "note-1"
    assert cards[0].likes == "1.2万"
\`\`\`

\`FakePage.evaluate\` returns the supplied list; the test has no browser, network, cookie, or QR dependency.

- [ ] **Step 2: Run RED**

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/collection/test_xiaohongshu_dom_adapter.py -v\`  
Expected: FAIL because the gateway is absent.

- [ ] **Step 3: Implement bounded local-only gateway**

\`\`\`python
class XiaohongshuBrowserGateway:
    SEARCH_URL = "https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_explore_feed"

    def search(self, keyword: str) -> list[PublicSearchCard]:
        try:
            with self._open_signed_in_page() as page:
                page.goto(self.SEARCH_URL.format(keyword=quote(keyword)), wait_until="domcontentloaded", timeout=20_000)
                page.wait_for_selector("section.note-item, a[href*='/explore/']", timeout=12_000)
                return self.extract_cards(page)
        except Exception as error:
            raise XiaohongshuCollectionError(self._safe_message(error)) from error
\`\`\`

\`_open_signed_in_page\` imports \`xhs_cli.auth.load_cookie\` and \`camoufox.sync_api.Camoufox\`, injects the returned session only into the transient page context, and always closes the context. It must not log, return, write, or interpolate a session value into an exception. \`extract_cards\` uses one \`page.evaluate\` function over visible card links/text, caps at 20 complete cards, and never reads \`window.__INITIAL_STATE__\`.

Add the verified runtime pins to \`backend/requirements.txt\`:

\`\`\`text
camoufox==0.4.11
xhs-cli==0.1.4
\`\`\`

- [ ] **Step 4: Run GREEN without launching a real browser**

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/collection/test_xiaohongshu_dom_adapter.py -v\`  
Expected: PASS.

- [ ] **Step 5: Commit**

\`\`\`powershell
git add backend/app/collection/xiaohongshu_browser_gateway.py backend/app/collection/xiaohongshu_dom_adapter.py backend/requirements.txt backend/tests/collection/test_xiaohongshu_dom_adapter.py
git commit -m "feat: collect Xiaohongshu search cards from local session"
\`\`\`

### Task 3: Expose a credential-safe collection endpoint

**Files:**
- Modify: \`backend/app/collection/router.py\`
- Modify: \`backend/tests/collection/test_fixture_import.py\`

- [ ] **Step 1: Write a failing route test**

\`\`\`python
class FakeDomAdapter(FakeRedbookAdapter):
    @property
    def name(self) -> str:
        return "xiaohongshu-dom"


def test_xiaohongshu_import_uses_collection_service(client, project, monkeypatch) -> None:
    monkeypatch.setattr(collection_router, "XiaohongshuDomAdapter", FakeDomAdapter)
    response = client.post(f"/api/projects/{project['id']}/collections/xiaohongshu?keyword=敏感肌")
    assert response.status_code == 201
    assert response.json()["notes_created"] == 1
\`\`\`

- [ ] **Step 2: Run RED**

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/collection/test_fixture_import.py::test_xiaohongshu_import_uses_collection_service -v\`  
Expected: FAIL because the route is absent.

- [ ] **Step 3: Implement the route and error mapping**

\`\`\`python
def xiaohongshu_service(session: Session) -> CollectionService:
    return CollectionService(session, XiaohongshuDomAdapter(XiaohongshuBrowserGateway()))


@router.post("/collections/xiaohongshu", response_model=CollectionSummary, status_code=status.HTTP_201_CREATED)
def import_xiaohongshu(project_id: str, keyword: str, session: Session = Depends(get_session)) -> CollectionSummary:
    try:
        return xiaohongshu_service(session).import_keyword(project_id, keyword)
    except XiaohongshuCollectionError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
\`\`\`

- [ ] **Step 4: Add a redacted error test, prove RED then GREEN**

\`\`\`python
def test_xiaohongshu_import_returns_safe_error(client, project, monkeypatch) -> None:
    monkeypatch.setattr(collection_router, "XiaohongshuDomAdapter", FailingDomAdapter)
    response = client.post(f"/api/projects/{project['id']}/collections/xiaohongshu?keyword=敏感肌")
    assert response.status_code == 422
    assert "cookie" not in response.text.lower()
\`\`\`

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/collection/test_fixture_import.py -v\`  
Expected: new test fails before error mapping, then all collection API tests PASS.

- [ ] **Step 5: Commit**

\`\`\`powershell
git add backend/app/collection/router.py backend/tests/collection/test_fixture_import.py
git commit -m "feat: expose Xiaohongshu keyword collection route"
\`\`\`

### Task 4: Add real-source controls and imported-note preview

**Files:**
- Create: \`frontend/src/components/XiaohongshuImport.tsx\`
- Create: \`frontend/src/components/NotesPreview.tsx\`
- Modify: \`frontend/src/api/types.ts\`
- Modify: \`frontend/src/api/client.ts\`
- Modify: \`frontend/src/App.tsx\`
- Modify: \`frontend/src/App.test.tsx\`
- Modify: \`frontend/src/styles.css\`

- [ ] **Step 1: Write a failing user-flow test**

\`\`\`tsx
it("imports a Xiaohongshu keyword before analysis", async () => {
  const user = userEvent.setup();
  const api = { ...fakeApi, importXiaohongshu: async () => ({ run_id: "xhs-run", status: "succeeded", notes_created: 4, metric_snapshots_created: 4 }) };
  render(<App api={api} />);
  await createProject(user);
  await user.type(screen.getByLabelText("小红书关键词"), "敏感肌");
  await user.click(screen.getByRole("button", { name: "采集公开搜索结果" }));
  expect(await screen.findByText("已导入 4 条公开笔记")).toBeInTheDocument();
});

async function createProject(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText("项目名称"), "护肤直播增长");
  await user.click(screen.getByRole("button", { name: "创建项目" }));
}
\`\`\`

- [ ] **Step 2: Run RED**

Run: \`cd frontend; npm test -- App.test.tsx\`  
Expected: FAIL because the API and UI do not exist.

- [ ] **Step 3: Implement the API and minimal control**

\`\`\`ts
importXiaohongshu(projectId: string, keyword: string) {
  return request(\`/projects/\${projectId}/collections/xiaohongshu?keyword=\${encodeURIComponent(keyword)}\`, { method: "POST" });
}
\`\`\`

\`\`\`tsx
export function XiaohongshuImport({ enabled, onImport }: Props) {
  const [keyword, setKeyword] = useState("");
  return <section className="panel">
    <label htmlFor="xhs-keyword">小红书关键词</label>
    <input id="xhs-keyword" value={keyword} onChange={(event) => setKeyword(event.target.value)} disabled={!enabled} />
    <button disabled={!enabled || !keyword.trim()} onClick={() => onImport(keyword.trim())}>采集公开搜索结果</button>
  </section>;
}
\`\`\`

Add \`importXiaohongshu(projectId, keyword): Promise<CollectionSummary>\` to \`Api\`. In \`App\`, send success to existing \`summary\` state to enable ranking, display \`已导入 {notes_created} 条公开笔记\`, and state that collection uses the user's local signed-in session.

- [ ] **Step 4: Run GREEN**

Run: \`cd frontend; npm test -- App.test.tsx\`  
Expected: PASS.

- [ ] **Step 5: Add a failure-state test before wiring it**

\`\`\`tsx
it("shows the safe collection error", async () => {
  const api = { ...fakeApi, importXiaohongshu: async () => { throw new Error("请在本机完成登录后重试"); } };
  const user = userEvent.setup();
  render(<App api={api} />);
  await createProject(user);
  await user.type(screen.getByLabelText("小红书关键词"), "敏感肌");
  await user.click(screen.getByRole("button", { name: "采集公开搜索结果" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("请在本机完成登录后重试");
});
\`\`\`

- [ ] **Step 6: Use the existing App guard to make that test GREEN, then add note preview**

Add \`listNotes(projectId)\` to \`Api\` and \`NotesPreview\`. Render at most ten notes with title, author, likes/favorites, source adapter, and an external note link using \`target="_blank" rel="noreferrer"\`. Add a test that a note title appears after successful import.

- [ ] **Step 7: Run all frontend checks and commit**

Run: \`cd frontend; npm test; npm run build\`  
Expected: all tests PASS and the TypeScript/Vite build succeeds.

\`\`\`powershell
git add frontend/src
git commit -m "feat: add Xiaohongshu keyword import workbench"
\`\`\`

### Task 5: Document and verify the feature

**Files:**
- Modify: \`README.md\`
- Modify: \`.gitignore\`
- Modify: \`docs/superpowers/specs/2026-07-13-xiaohongshu-dom-collection-design.md\`

- [ ] **Step 1: Document local setup and boundaries**

Add: install \`backend/requirements.txt\`; install the matching Camoufox browser binary; run \`xhs login\` once; create a project; collect a keyword; run ranking. State clearly that the feature is read-only, requires manual login/verification resolution, and must not be used to bypass platform controls.

- [ ] **Step 2: Ignore local artifacts**

\`\`\`gitignore
.superpowers/
xhs-login-qr.png
.tmp-xhs-*
camoufox-*.zip
showcase/xhs-search-preview.png
\`\`\`

- [ ] **Step 3: Run full regression**

Run: \`cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests -v\`  
Expected: all backend tests PASS.

Run: \`cd frontend; npm test; npm run build\`  
Expected: all frontend tests PASS and build succeeds.

- [ ] **Step 4: Do the local-only manual verification**

With the existing local session, call \`POST /api/projects/{project_id}/collections/xiaohongshu?keyword=敏感肌\`. Verify 201, a nonzero count, imported notes with \`source.adapter == "xiaohongshu-dom"\`, and a successful \`POST /analysis/rank\`. Never record cookies, QR data, browser logs, or screenshots in Git.

- [ ] **Step 5: Commit verified implementation and documentation**

\`\`\`powershell
git add README.md .gitignore docs backend frontend
git commit -m "docs: document local Xiaohongshu collection setup"
\`\`\`
