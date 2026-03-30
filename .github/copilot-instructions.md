# GENERAL RULES

- All code must be written in English.
- All functions must include explicit type hints for parameters and return values.
- Write consistent and clear docstrings (pydoc style) following the existing project conventions.
- Use self-explanatory names for variables, functions, and parameters (e.g., is_valid, user_id, has_permission).
- Follow PEP8 and prioritize readability over cleverness.
- Avoid code duplication and keep functions small and focused (single responsibility).

--------------------------------------------------

## ARCHITECTURE RULES (MANDATORY)

- Follow the defined project structure from the roadmap (ANALISIS_Y_HOJA_DE_RUTA.md file).
- Respect layer separation:
  - API (routers): only HTTP/WebSocket handling
  - Services: business logic
  - Repositories: database access
  - Schemas: Pydantic models
  - Game: pure domain logic (must remain framework-independent)

- NEVER place business logic inside FastAPI endpoints.
- The game logic (Barco, Tablero, Partida, etc.) must remain decoupled from FastAPI and the database.

--------------------------------------------------

## MIGRATION CONTEXT (CRITICAL)

- This project is a migration from a CLI-based Python application to FastAPI + Vue.
- Existing game logic must be reused whenever possible.
- DO NOT rewrite working logic unless strictly necessary.
- If changes are required, clearly explain why in comments or docstrings.
- Maintain functional parity with the original implementation.

--------------------------------------------------

## FASTAPI & BACKEND RULES

- Use Pydantic models for all request/response validation.
- Use proper HTTP status codes and FastAPI conventions.
- Handle errors explicitly using HTTPException.
- Use dependency injection (Depends) for shared logic (e.g., authentication).
- Keep endpoints thin and delegate logic to services.

--------------------------------------------------

## WEBSOCKET RULES

- WebSocket communication must follow the structure defined in the roadmap.
- Replace the TCP protocol with structured Pydantic message models.
- Validate all incoming messages.
- The server must always be the source of truth for game state.
- Handle disconnections and edge cases explicitly.

--------------------------------------------------

## DATABASE RULES

- Use SQLAlchemy 2.0 (async).
- Use PostgreSQL as the database.
- Keep database logic inside repositories or services.
- Do not mix ORM models with Pydantic schemas.
- Ensure consistency between DB models and API schemas.

--------------------------------------------------

## TESTING RULES

- Use pytest for all tests.
- Write unit tests for services and game logic.
- Write integration tests for API and WebSocket flows when applicable.
- Cover edge cases and failure scenarios.

--------------------------------------------------

## FRONTEND AWARENESS (IMPORTANT)

- Ensure API responses are consistent and predictable for Vue frontend consumption.
- Do not introduce breaking changes in API contracts without updating schemas.
- Use clear and stable response structures.

--------------------------------------------------

## ROADMAP (ANALISIS_Y_HOJA_DE_RUTA.MD FILE) RULES (CRITICAL)

- The ANALISIS_Y_HOJA_DE_RUTA.md file is the single source of truth for project progress.

Whenever a phase or task is implemented:

- Update the corresponding section in the ANALISIS_Y_HOJA_DE_RUTA.md file.
- Mark completed tasks clearly (e.g., [x]).
- Add a short description of what was implemented.
- Document important decisions and deviations from the original plan.
- Keep the structure of phases intact.
- Ensure the document reflects the real current state of the project.

- The ANALISIS_Y_HOJA_DE_RUTA.md file must serve both as:
  - a roadmap (planned work)
  - and a progress log (completed work + context)

--------------------------------------------------

## DECISION-MAKING RULES

- Prefer consistency with the existing codebase over introducing new patterns.
- Prefer explicitness over implicit behavior.
- When in doubt, follow the architecture defined in the ANALISIS_Y_HOJA_DE_RUTA.md file.
