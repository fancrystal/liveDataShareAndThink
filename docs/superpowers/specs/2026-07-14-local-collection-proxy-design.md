# Local Xiaohongshu Collection Proxy Design

## Goal

Let the Docker-hosted Phase 1 page trigger a Xiaohongshu public-search collection while keeping the existing `xhs-cli` login session, including its Cookie, on the Windows host only. Keep a command-line fallback for diagnosis and manual collection.

## Scope

- Add a host-only FastAPI companion service on port `17779`.
- Reuse the existing `XiaohongshuBrowserGateway`; it is the only component allowed to access `xhs-cli` session data.
- Let the Docker API ask the companion for normalized public search cards, then persist them through the existing `CollectionService`.
- Keep direct local collection working when the main API is run outside Docker.
- Display collection progress and a useful local-proxy failure message in the existing React page.
- Supply a command that starts the companion service.

Out of scope: Docker-internal browser login, cookie export/import, automated platform interactions, note-detail crawling, and Phase 2 livestream replay.

## Architecture

`17777 web -> 17778 Docker API -> host.docker.internal:17779 proxy -> xhs-cli session -> Xiaohongshu`.

The proxy exposes only `POST /api/collections/xiaohongshu/search`. The Docker API sends an `X-Collection-Proxy-Token` header and receives the existing `PublicSearchCard` structure. The proxy binds to `0.0.0.0` only because Docker Desktop reaches the host through its gateway; it accepts requests only with an explicitly configured random token. No endpoint returns, stores, or logs Cookie values.

The main API selects its gateway from configuration:

- `COLLECTION_PROXY_URL` unset: use the current local `XiaohongshuBrowserGateway`.
- `COLLECTION_PROXY_URL` set: use an HTTP gateway that calls the host companion.

Docker sets the URL to `http://host.docker.internal:17779`. The shared token exists in the user-owned `.env`, is omitted from `.env.example`, and is never included in client-side build arguments.

## Components

- `backend/app/collection/proxy_app.py`: small host companion FastAPI app; validates token and delegates to `XiaohongshuBrowserGateway`.
- `backend/app/collection/xiaohongshu_proxy_gateway.py`: HTTP implementation of `SearchGateway`; validates response shape and turns transport failures into credential-safe `XiaohongshuCollectionError` messages.
- `backend/app/collection/gateway_factory.py`: chooses direct-browser or proxy gateway once from Settings.
- `backend/app/collection/router.py`: uses the factory rather than constructing the direct gateway inline.
- `backend/app/core/config.py`: adds proxy URL/token settings.
- `backend/app/collection/proxy_runner.py`: executable module for `python -m app.collection.proxy_runner`.
- `docker-compose.yml`: passes only proxy URL and token to the API container.
- React import component: disables duplicate clicks, gives visible progress, and explains how to start the host proxy after a proxy-unavailable error.

## API and Failure Behaviour

The proxy accepts `{ "keyword": "..." }`, rejects blank keywords with 422, rejects a missing/wrong token with 401, and returns a list of public card objects. Platform/session failures remain generic and do not leak exception details or credentials.

The HTTP gateway maps connection failures to: “本地采集代理未启动。请在项目目录运行启动命令后重试。” It maps 401 to a configuration mismatch message and forwards safe 422 platform errors. The existing main API continues to return 422, so the browser receives the same error contract.

## Testing

- Proxy API tests cover token rejection, blank keyword rejection, and successful delegation with an injected fake gateway.
- HTTP gateway tests cover request token/header, normalized response conversion, unavailable proxy, 401, and 422 messages with mocked HTTP transport.
- Factory tests cover direct and proxy selection.
- Frontend test verifies the button shows a collecting state and prevents a second import while pending.
- Existing backend suite and frontend build/test remain green.

## Operational Use

1. Put a long random `COLLECTION_PROXY_TOKEN` in local `.env`.
2. Start `python -m app.collection.proxy_runner` on the Windows host with `PYTHONPATH=backend`.
3. Start Docker with `docker compose -f docker-compose.yml up -d --build`.
4. Use the `17777` page normally. The login session is maintained through `xhs login` on the host, not in Docker.

