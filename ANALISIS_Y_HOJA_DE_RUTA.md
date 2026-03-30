# Project Analysis and Roadmap: Migration to FastAPI + Vue

## 1. Current project state analysis

### 1.1 Executive summary

**Hundir la Flota** (Battleship) is a game implemented in pure Python (no external dependencies) with MVC architecture, support for PvE (against AI) and PvP (multiplayer over TCP sockets with asyncio) matches. The current interface is console-based.

### 1.2 Current tech stack

| Layer                 | Technology                         |
| --------------------- | ---------------------------------- |
| Language              | Python 3.13                        |
| UI                    | Console (stdin/stdout)             |
| Networking            | TCP sockets + asyncio              |
| Protocol              | JSON delimited by `\n`             |
| Persistence           | None (all in memory)               |
| Testing               | pytest + pytest-asyncio + coverage |
| External dependencies | None (stdlib only)                 |

### 1.3 Current architecture

```text
┌─────────────────────────────────────────────────────┐
│                    App (app.py)                      │
│           Entry point + orchestration                │
├──────────────┬──────────────┬───────────────────────┤
│     View     │  Controller  │       Net             │
│  (console)   │  (PvE/PvP)   │  (TCP sockets)        │
├──────────────┴──────────────┴───────────────────────┤
│                  Services                            │
│          (GameService - intermediate layer)          │
├─────────────────────────────────────────────────────┤
│                    Model                             │
│     Ship · Board · Game (PvE/PvP)                   │
├─────────────────────────────────────────────────────┤
│                    Config                            │
│   Constants · Texts · Log events                    │
└─────────────────────────────────────────────────────┘
```

**Main components:**

- **Model** (`model/`): Ship, Board, Game (abstract), PvEGame, PvPGame with states (PLACEMENT → PLAYING → FINISHED). Pure game logic with no external dependencies.
- **View** (`view/`): View abstraction + ConsoleView implementation + menus. Easy to replace thanks to the abstract interface.
- **Controller** (`controller/`): PvEController (synchronous local loop) and PvPClientController (async loop with message dispatch).
- **Net** (`net/`): ClientSocket (async TCP), Server (matchmaking with queue + 15s timeout), PvPSession (server-side game management), protocol with 16 JSON message types.
- **Services** (`services/`): GameService as an intermediate layer between net and model.

### 1.4 Current PvP network protocol

The protocol defines 16 message types (WAIT, START, SHIP_LIST, SELECT_SHIP, CONFIRMATION, TURN, SHOT, RESULT, RECEIVED, BOARD_STATE, ERROR, END, ABANDON, EXIT, CONNECTION_CLOSED, QUEUE_TIMEOUT) over TCP with JSON per line.

The flow is: **connection → waiting queue → matchmaking → ship placement → shooting turns → end**.

### 1.5 Strengths

1. **Flawless separation of concerns**: The model knows nothing about the UI or the network. The view is abstract. Controllers use dependency injection.
2. **Extensible design**: Abstract classes (Game, View, Controller) respect Open/Closed — new implementations can be added without modifying existing ones.
3. **Async networking**: Correct use of asyncio with locks, disconnection handling and timeouts.
4. **Solid testing**: 11 unit test files with parameterization, async mocks and coverage.
5. **Well-defined protocol**: TypedDict for messages, enums for finite states.

### 1.6 Weaknesses and gaps

1. **No persistence**: No database or any kind of storage.
2. **No authentication**: Any TCP client can connect to the server.
3. **No history**: No match records, results or statistics.
4. **Limited interface**: Console only, no web experience.
5. **No reconnection**: If a player disconnects, the match is lost.
6. **Protocol coupled to TCP**: Non-standard, requires a special client.
7. **No incoming message validation**: Potential vulnerability to malformed messages.

---

## 2. Professional opinion on the stack choice

### 2.1 FastAPI + Vue? Yes, with nuances

The **FastAPI + Vue** combination is a solid choice for this project for the following reasons:

| Aspect                            | Fits?        | Reason                                                                                          |
| --------------------------------- | ------------ | ----------------------------------------------------------------------------------------------- |
| REST API for users, auth, history | ✅ Excellent | FastAPI is ideal for REST APIs with automatic validation (Pydantic), OpenAPI docs, native async |
| Real-time communication (PvP)     | ✅ Good      | FastAPI natively supports WebSockets, replacing the custom TCP protocol                         |
| Interactive frontend              | ✅ Excellent | Vue is lightweight, reactive, ideal for game UIs with dynamic state                             |
| Reuse of current model            | ✅ Excellent | Game logic (Ship, Board, Game) is pure Python → integrates directly                             |
| Reuse of current service          | ✅ Good      | GameService adapts well as a service layer behind the API                                       |

### 2.2 Alternatives considered

| Alternative stack                  | Verdict                | Reason                                                                                                                                                                                                                            |
| ---------------------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Django + Vue**                   | ⚠️ Viable but overkill | Django brings ORM, admin, auth built-in. But it's synchronous by default, heavier. For a game with WebSockets, Django Channels adds unnecessary complexity. FastAPI is more natural for async + WebSockets.                       |
| **Flask + Vue**                    | ⚠️ Inferior            | Flask has no native async support, no built-in WebSockets. Requires extensions (Flask-SocketIO). Less validation, less auto-generated docs.                                                                                       |
| **FastAPI + React**                | ✅ Equivalent          | React is equally valid but more ceremonial. Vue is more accessible, has a better learning curve and for a project of this size, less boilerplate. Both are excellent; Vue is the right choice if you're already familiar with it. |
| **FastAPI + Svelte**               | ✅ Interesting         | Svelte generates lighter and more reactive code. But its ecosystem is smaller and the community is more limited. For a first web project, Vue offers better support and documentation.                                            |
| **Node.js (Express/NestJS) + Vue** | ❌ Not recommended     | Requires rewriting all game logic in JavaScript/TypeScript. The current Python model is clean, tested and functional — there's no reason to discard it.                                                                           |

### 2.3 Final recommendation

**FastAPI + Vue is the optimal choice for this case.** Concrete reasons:

1. **FastAPI is async-native**: The project already uses asyncio extensively. Migrating from TCP sockets to FastAPI WebSockets is organic.
2. **Pydantic replaces TypedDicts**: Protocol messages (`MessageType`) migrate directly to Pydantic models with automatic validation.
3. **Free OpenAPI docs**: FastAPI generates interactive documentation (Swagger/ReDoc) for the auth and history API.
4. **Game model is fully reusable**: Ship, Board, Game, PvEGame, PvPGame → integrate as-is.
5. **Native WebSockets**: FastAPI + Starlette handle WebSockets simply, replacing the custom TCP server.
6. **Vue is ideal for the frontend**: Reactive state for boards, composables for WebSocket, lightweight and excellent DX.

**An important note:** for real-time PvP communication, the key is migrating from **raw TCP sockets** to **WebSockets**. This greatly simplifies the infrastructure: a single HTTP/WS server handles both the REST API (auth, history) and game communication (WebSockets).

---

## 3. Technical design decisions

### 3.1 Database

| Option                      | Recommendation                                  |
| --------------------------- | ----------------------------------------------- |
| **SQLite** (development)    | ✅ Perfect to start with, no configuration      |
| **PostgreSQL** (production) | ✅ Recommended long-term                        |
| **ORM**                     | SQLAlchemy 2.0 (async) + Alembic for migrations |

### 3.2 Authentication

| Option                    | Recommendation                                          |
| ------------------------- | ------------------------------------------------------- |
| **JWT (JSON Web Tokens)** | ✅ Stateless, ideal for API + WebSockets                |
| Library                   | `python-jose` + `passlib[bcrypt]`                       |
| Strategy                  | Access token (short-lived) + Refresh token (long-lived) |

### 3.3 Proposed data model

```
┌────────────────┐       ┌─────────────────────┐
│      User      │       │       Match          │
├────────────────┤       ├─────────────────────┤
│ id (PK)        │       │ id (PK)              │
│ username       │  1──N │ type (PVE/PVP)       │
│ email          │◄──────│ player1_id (FK)      │
│ password_hash  │◄──────│ player2_id (FK|null) │
│ created_at     │       │ winner_id (FK|null)   │
│ avatar_url     │       │ status               │
│ elo_rating     │       │ difficulty (PVE)     │
└────────────────┘       │ created_at           │
                         │ finished_at          │
                         │ duration_seconds     │
                         │ shots_p1             │
                         │ shots_p2             │
                         └─────────────────────┘

┌──────────────────────┐
│     UserStats        │
├──────────────────────┤
│ user_id (FK, PK)     │
│ pve_wins             │
│ pve_losses           │
│ pvp_wins             │
│ pvp_losses           │
│ abandons             │
│ total_shots          │
│ ships_sunk           │
│ current_streak       │
│ best_streak          │
└──────────────────────┘
```

### 3.4 API endpoint structure

```
AUTH
  POST   /api/auth/register          → Create account
  POST   /api/auth/login             → Get JWT tokens
  POST   /api/auth/refresh           → Renew access token
  POST   /api/auth/logout            → Invalidate refresh token

USERS
  GET    /api/users/me               → Authenticated user profile
  PUT    /api/users/me               → Update profile
  GET    /api/users/me/stats         → User statistics
  GET    /api/users/{id}/profile     → Public profile of another user
  GET    /api/users/ranking          → General ranking (by ELO or wins)

MATCHES
  GET    /api/matches/history        → Authenticated user match history
  GET    /api/matches/{id}           → Match details

GAME (WebSockets)
  WS     /ws/pve                     → Match against the AI
  WS     /ws/pvp                     → Matchmaking + PvP match
```

---

## 4. Roadmap

### Phase 0: Environment setup (preliminary step)

- [ ] **0.1** Create `feature/web-migration` branch in Git.
- [ ] **0.2** Define folder structure for the new project:
  ```
  hundir_la_flota/
  ├── backend/                    # FastAPI
  │   ├── app/
  │   │   ├── main.py             # FastAPI entry point
  │   │   ├── core/
  │   │   │   ├── config.py       # Settings (Pydantic BaseSettings)
  │   │   │   ├── security.py     # JWT, password hashing
  │   │   │   └── database.py     # SQLAlchemy engine, session
  │   │   ├── models/             # SQLAlchemy models (User, Match)
  │   │   ├── schemas/            # Pydantic schemas (request/response)
  │   │   ├── api/
  │   │   │   ├── auth.py         # Auth endpoints
  │   │   │   ├── users.py        # User endpoints
  │   │   │   ├── matches.py      # History endpoints
  │   │   │   └── deps.py         # Dependencies (get_current_user, etc.)
  │   │   ├── ws/
  │   │   │   ├── manager.py      # ConnectionManager for WebSockets
  │   │   │   ├── pve.py          # WS endpoint for PvE
  │   │   │   └── pvp.py          # WS endpoint for PvP + matchmaking
  │   │   ├── services/           # Business logic
  │   │   └── game/               # ← Reused game logic
  │   │       ├── ship.py         # Migrated directly
  │   │       ├── board.py        # Migrated directly
  │   │       ├── game.py         # Migrated/adapted
  │   │       ├── pve_game.py
  │   │       └── pvp_game.py
  │   ├── migrations/             # Alembic
  │   ├── tests/
  │   ├── requirements.txt
  │   └── alembic.ini
  │
  ├── frontend/                   # Vue 3
  │   ├── src/
  │   │   ├── views/              # Pages (Login, Lobby, Game, Profile)
  │   │   ├── components/         # Components (Board, Ship, Cell, etc.)
  │   │   ├── composables/        # Reusable logic (useWebSocket, useAuth)
  │   │   ├── stores/             # Pinia (global state: auth, game)
  │   │   ├── router/             # Vue Router
  │   │   └── api/                # HTTP client (axios/fetch)
  │   ├── package.json
  │   └── vite.config.js
  │
  └── docker-compose.yml          # Optional: DB + backend + frontend
  ```
- [ ] **0.3** Install base backend dependencies:
  ```
  fastapi uvicorn[standard] sqlalchemy[asyncio] alembic
  aiosqlite asyncpg python-jose[cryptography] passlib[bcrypt]
  pydantic-settings python-multipart
  ```
- [ ] **0.4** Initialize frontend with Vue 3:
  ```
  npm create vue@latest frontend -- --typescript --router --pinia
  ```

---

### Phase 1: Backend — Database and authentication

- [ ] **1.1** Configure SQLAlchemy async + create `database.py` with engine and `AsyncSession`.
- [ ] **1.2** Define SQLAlchemy models: `User`, `Match`, `UserStats`.
- [ ] **1.3** Configure Alembic and generate the initial migration.
- [ ] **1.4** Implement `security.py`: hashing functions (`passlib`) and JWT (`python-jose`).
- [ ] **1.5** Create Pydantic schemas: `UserCreate`, `UserResponse`, `TokenResponse`, `LoginRequest`.
- [ ] **1.6** Implement auth endpoints: `POST /register`, `POST /login`, `POST /refresh`.
- [ ] **1.7** Implement `get_current_user` dependency to protect routes.
- [ ] **1.8** Unit tests for auth (register, login, invalid token, refresh).

---

### Phase 2: Backend — Users API and statistics

- [ ] **2.1** Endpoint `GET /users/me` — return authenticated user profile.
- [ ] **2.2** Endpoint `PUT /users/me` — update profile (username, avatar).
- [ ] **2.3** Endpoint `GET /users/me/stats` — wins, losses, streak, etc.
- [ ] **2.4** Endpoint `GET /users/{id}/profile` — public profile.
- [ ] **2.5** Endpoint `GET /users/ranking` — top players sorted by ELO or wins.
- [ ] **2.6** Unit tests for all user endpoints.

---

### Phase 3: Backend — Migrate game logic

- [ ] **3.1** Copy `Ship`, `Board`, `ShotResult` to `backend/app/game/` — no modifications.
- [ ] **3.2** Adapt `PvEGame` to work as an isolated component (no console dependency).
- [ ] **3.3** Adapt `PvPGame` to work over WebSockets instead of TCP sockets.
- [ ] **3.4** Migrate `GameService` as a backend service.
- [ ] **3.5** Define WS protocol messages as Pydantic models (replace TypedDicts).
- [ ] **3.6** Unit tests for the migrated game logic (reuse existing tests adapted).

---

### Phase 4: Backend — WebSockets for real-time matches

- [ ] **4.1** Create `ConnectionManager` — management of active WS connections, per user.
- [ ] **4.2** Implement `WS /ws/pve`:
  - Authenticate via token (query param or first message).
  - Create `PvEGame` server-side.
  - Loop: receive shot → process → send result + board state.
  - On finish: record result in DB.
- [ ] **4.3** Implement `WS /ws/pvp`:
  - Authenticate via token.
  - Matchmaking queue (equivalent to current `waiting_queue`).
  - On match: create `PvPSession` (adapt existing one).
  - Loop: placement phase → turn phase → end.
  - On finish: record result in DB + update stats.
- [ ] **4.4** Handle disconnections and abandons (equivalent to `player_disconnected`).
- [ ] **4.5** Integration tests for full WS flow (connection → match → end).

---

### Phase 5: Backend — Match history

- [ ] **5.1** `MatchDBService` — create record in DB when match starts, update on finish.
- [ ] **5.2** Endpoint `GET /matches/history` — list user matches with pagination.
- [ ] **5.3** Endpoint `GET /matches/{id}` — match details (players, result, duration, shots).
- [ ] **5.4** Stats service — update `UserStats` after each match.
- [ ] **5.5** Tests.

---

### Phase 6: Frontend — Base structure and authentication

- [ ] **6.1** Configure Vue 3 + TypeScript + Vite + Vue Router + Pinia project.
- [ ] **6.2** Create auth store (`useAuthStore`): login, register, logout, token management.
- [ ] **6.3** Configure HTTP interceptor (axios or fetch wrapper) to automatically inject JWT.
- [ ] **6.4** Create views: `LoginView`, `RegisterView` with forms.
- [ ] **6.5** Implement route guards (redirect to login if not authenticated).
- [ ] **6.6** Base layout: navbar with user, main navigation.

---

### Phase 7: Frontend — Lobby and profile

- [ ] **7.1** `LobbyView` — buttons to start PvE (difficulty selection) or PvP.
- [ ] **7.2** `ProfileView` — show statistics, match history, avatar.
- [ ] **7.3** `RankingView` — leaderboard table.
- [ ] **7.4** `MatchHistory` component — paginated list of matches with results.

---

### Phase 8: Frontend — Game interface

- [ ] **8.1** `useGameWebSocket` composable — connect to WS, send/receive messages, manage state.
- [ ] **8.2** `GameBoard` component — interactive board (NxN grid, clickable cells).
- [ ] **8.3** `ShipPlacement` component — drag/rotate ships onto the board.
- [ ] **8.4** `GameCell` component — individual cell with visual states (empty, water, hit, sunk, own ship).
- [ ] **8.5** `GameStatus` component — current turn, shots, server messages.
- [ ] **8.6** `PveGameView`:
  - Connect to WS `/ws/pve`.
  - Difficulty selection → auto placement → shooting phase.
  - Show opponent board + remaining shots.
  - Result screen (victory/defeat).
- [ ] **8.7** `PvpGameView`:
  - Connect to WS `/ws/pvp`.
  - Waiting screen (matchmaking).
  - Manual ship placement phase.
  - Turn phase (own board + opponent board).
  - Turn indicator, shot results.
  - Final result screen.
- [ ] **8.8** Animations and visual feedback: shots into water, impacts, ships sinking.

---

### Phase 9: Integration and E2E testing

- [ ] **9.1** Configure CORS in FastAPI to allow frontend requests.
- [ ] **9.2** E2E tests: full flow register → login → PvE → view history.
- [ ] **9.3** E2E tests: full flow login → PvP matchmaking → match → result.
- [ ] **9.4** Test disconnections, timeouts, expired tokens.
- [ ] **9.5** Security review: input validation, rate limiting, sanitization.

---

### Phase 10: Polish and deployment

- [ ] **10.1** Dockerize: Dockerfile for backend + frontend + docker-compose with DB.
- [ ] **10.2** Environment variables for configuration (SECRET_KEY, DATABASE_URL, etc.).
- [ ] **10.3** API documentation (FastAPI generates it automatically at `/docs`).
- [ ] **10.4** Updated README with installation and running instructions.
- [ ] **10.5** Basic CI/CD (GitHub Actions: lint + tests on each push).

---

## 5. Current code reuse mapping

One of the greatest assets of the current project is that **the game logic is completely independent from the interface and the network**. This enables an efficient migration:

| Current component           | Destination in the new stack           | Action                                      |
| --------------------------- | -------------------------------------- | ------------------------------------------- |
| `model/ship.py`             | `backend/app/game/ship.py`             | Copy without changes                        |
| `model/board.py`            | `backend/app/game/board.py`            | Copy without changes                        |
| `model/result.py`           | `backend/app/game/result.py`           | Copy without changes                        |
| `model/game/game.py`        | `backend/app/game/game.py`             | Copy without changes                        |
| `model/game/pve_game.py`    | `backend/app/game/pve_game.py`         | Copy without changes                        |
| `model/game/pvp_game.py`    | `backend/app/game/pvp_game.py`         | Copy without changes                        |
| `services/game_service.py`  | `backend/app/services/game_service.py` | Adapt minimally                             |
| `config/constants.py`       | `backend/app/core/game_config.py`      | Copy, possibly migrate to Pydantic Settings |
| `net/protocol/messages.py`  | `backend/app/schemas/ws_messages.py`   | Migrate TypedDicts → Pydantic models        |
| `net/server/pvp_session.py` | `backend/app/ws/pvp.py`                | Adapt from TCP to WebSocket                 |
| `net/server/server.py`      | `backend/app/ws/manager.py`            | Adapt matchmaking to WS                     |
| `view/`                     | `frontend/`                            | Rewrite in Vue (console is discarded)       |
| `controller/`               | Dissolved into API + WS handlers       | Controller logic is distributed             |
| `tests/unit/model/`         | `backend/tests/unit/game/`             | Reuse adapting imports                      |
| `tests/unit/net/`           | `backend/tests/unit/ws/`               | Rewrite for WebSockets                      |

**~60% of the Python code is reused directly or with minimal adaptations.**

---

## 6. Phase priorities and dependencies

```
Phase 0 (Setup)
  │
  ├──► Phase 1 (Auth + DB)
  │       │
  │       ├──► Phase 2 (Users API)
  │       │       │
  │       │       └──► Phase 5 (History)
  │       │
  │       └──► Phase 3 (Migrate game logic)
  │               │
  │               └──► Phase 4 (WebSockets)
  │                       │
  │                       └──► Phase 5 (History) ◄── also depends on Phase 2
  │
  └──► Phase 6 (Frontend base + auth) ◄── can be done in parallel with Phase 1
          │
          ├──► Phase 7 (Lobby + profile) ◄── requires Phases 2, 5
          │
          └──► Phase 8 (Game interface) ◄── requires Phase 4
                  │
                  └──► Phase 9 (E2E integration)
                          │
                          └──► Phase 10 (Deployment)
```

**Backend work (Phases 1-5) can be parallelized with frontend (Phases 6-8)** if there is availability to work on both simultaneously, using mocks on the frontend while the backend is being developed.

---

## 7. Risks and mitigations

| Risk                               | Impact          | Mitigation                                                                                    |
| ---------------------------------- | --------------- | --------------------------------------------------------------------------------------------- |
| WebSocket complexity in production | High            | Use robust `ConnectionManager`, disconnection tests, heartbeat/ping                           |
| State synchronization in PvP       | High            | Keep game logic server-side (the server is the source of truth)                               |
| WebSocket security                 | Medium          | Authenticate on WS handshake, validate each message with Pydantic                             |
| Matchmaking scalability            | Low (initially) | Current design (in-memory queue) works for hundreds of players. If it grows, migrate to Redis |
| DB performance                     | Low             | SQLite for development, PostgreSQL for production. Indexes on FKs                             |

---

## 8. Summary

The current project has a solid foundation with excellent separation of concerns. Migration to **FastAPI + Vue** is the right choice because:

- **FastAPI** is async-native like the current code, natively supports WebSockets, generates automatic API documentation, and Pydantic validates protocol messages in a superior way compared to TypedDict.
- **Vue 3** with Composition API offers ideal reactivity for rendering boards in real time, composables for WebSocket management, and is lightweight and accessible.
- **~60% of the Python code is reused** directly, especially all the game logic.
- Most of the new work is: database + auth + frontend + adapting TCP sockets to WebSockets.

The roadmap defines **10 concrete phases** with specific tasks, clear dependencies between phases, and opportunities for parallelization between backend and frontend.
