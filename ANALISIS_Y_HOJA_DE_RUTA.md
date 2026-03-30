# Análisis del Proyecto y Hoja de Ruta: Migración a FastAPI + Vue

## 1. Análisis del estado actual del proyecto

### 1.1 Resumen ejecutivo

**Hundir la Flota** es un juego de Battleship implementado en Python puro (sin dependencias externas) con arquitectura MVC, soporte para partidas PvE (contra IA) y PvP (multijugador en red vía sockets TCP con asyncio). La interfaz actual es por consola.

### 1.2 Stack tecnológico actual

| Capa                  | Tecnología                         |
| --------------------- | ---------------------------------- |
| Lenguaje              | Python 3.13                        |
| UI                    | Consola (stdin/stdout)             |
| Red                   | TCP sockets + asyncio              |
| Protocolo             | JSON delimitado por `\n`           |
| Persistencia          | Ninguna (todo en memoria)          |
| Testing               | pytest + pytest-asyncio + coverage |
| Dependencias externas | Ninguna (solo stdlib)              |

### 1.3 Arquitectura actual

```text
┌─────────────────────────────────────────────────────┐
│                    App (app.py)                      │
│         Punto de entrada + orquestación              │
├──────────────┬──────────────┬───────────────────────┤
│   Vista      │  Controlador │       Red             │
│  (consola)   │  (PvE/PvP)   │  (sockets TCP)        │
├──────────────┴──────────────┴───────────────────────┤
│                Servicios                             │
│          (PartidaService - capa intermedia)          │
├─────────────────────────────────────────────────────┤
│                    Modelo                            │
│     Barco · Tablero · Partida (PvE/PvP)             │
├─────────────────────────────────────────────────────┤
│                    Config                            │
│   Constantes · Textos · Eventos de log              │
└─────────────────────────────────────────────────────┘
```

**Componentes principales:**

- **Modelo** (`modelo/`): Barco, Tablero, Partida (abstracta), PartidaPVE, PartidaPVP con estados (COLOCACION → JUGANDO → FINALIZADA). Lógica de juego pura sin dependencias externas.
- **Vista** (`vista/`): Abstracción Vista + implementación VistaConsola + menús. Fácil de sustituir gracias a la interfaz abstracta.
- **Controlador** (`controlador/`): ControladorPVE (bucle síncrono local) y ControladorPVPCliente (bucle async con dispatch de mensajes).
- **Red** (`red/`): ClienteSocket (async TCP), Servidor (matchmaking con cola + timeout 15s), SesionPVP (gestión server-side de partida), protocolo de 16 tipos de mensajes JSON.
- **Servicios** (`servicios/`): PartidaService como capa intermedia entre red y modelo.

### 1.4 Protocolo de red PvP actual

El protocolo define 16 tipos de mensajes (ESPERA, INICIO, LISTA_BARCOS, SELECCIONAR_BARCO, CONFIRMACION, TURNO, DISPARO, RESULTADO, RECIBIDO, ESTADO_TABLEROS, ERROR, FIN, ABANDONO, SALIR, CIERRE_CONEXION, TIMEOUT_COLA) sobre TCP con JSON por línea.

El flujo es: **conexión → cola de espera → matchmaking → colocación de barcos → turnos de disparo → fin**.

### 1.5 Fortalezas

1. **Separación de responsabilidades impecable**: El modelo no sabe nada de la UI ni la red. La vista es abstracta. Los controladores usan inyección de dependencias.
2. **Diseño extensible**: Las clases abstractas (Partida, Vista, Controlador) respetan Open/Closed — se pueden añadir nuevas implementaciones sin modificar las existentes.
3. **Networking async**: Uso correcto de asyncio con locks, manejo de desconexiones y timeouts.
4. **Testing sólido**: 11 ficheros de tests unitarios con parametrización, mocks async y cobertura.
5. **Protocolo bien definido**: TypedDict para mensajes, enums para estados finitos.

### 1.6 Debilidades y carencias

1. **Sin persistencia**: No hay base de datos ni almacenamiento de ningún tipo.
2. **Sin autenticación**: Cualquier cliente TCP puede conectarse al servidor.
3. **Sin historial**: No se registran partidas, resultados ni estadísticas.
4. **Interfaz limitada**: Solo consola, sin experiencia web.
5. **Sin reconexión**: Si un jugador se desconecta, la partida se pierde.
6. **Protocolo acoplado a TCP**: No estándar, requiere cliente especial.
7. **Sin validación de mensajes entrantes**: Potencial vulnerabilidad a mensajes malformados.

---

## 2. Opinión profesional sobre la elección de stack

### 2.1 ¿FastAPI + Vue? Sí, con matices

La combinación **FastAPI + Vue** es una elección sólida para este proyecto por las siguientes razones:

| Aspecto                                 | ¿Encaja?     | Razón                                                                                            |
| --------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------ |
| API REST para usuarios, auth, historial | ✅ Excelente | FastAPI es ideal para APIs REST con validación automática (Pydantic), docs OpenAPI, async nativo |
| Comunicación en tiempo real (PvP)       | ✅ Bueno     | FastAPI soporta WebSockets nativamente, reemplaza el protocolo TCP custom                        |
| Frontend interactivo                    | ✅ Excelente | Vue es ligero, reactivo, ideal para UIs de juego con estado dinámico                             |
| Reutilización del modelo actual         | ✅ Excelente | La lógica de juego (Barco, Tablero, Partida) es pura Python → se integra directamente            |
| Reutilización del servicio actual       | ✅ Bueno     | PartidaService se adapta bien como capa de servicio detrás de la API                             |

### 2.2 Alternativas consideradas

| Stack alternativo                  | Veredicto               | Razón                                                                                                                                                                                                                                 |
| ---------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Django + Vue**                   | ⚠️ Viable pero excesivo | Django trae ORM, admin, auth integrados. Pero es síncrono por defecto, más pesado. Para un juego con WebSockets, Django Channels añade complejidad innecesaria. FastAPI es más natural para async + WebSockets.                       |
| **Flask + Vue**                    | ⚠️ Inferior             | Flask no tiene soporte async nativo, ni WebSockets integrados. Requiere extensiones (Flask-SocketIO). Menos validación, menos docs automáticas.                                                                                       |
| **FastAPI + React**                | ✅ Equivalente          | React es igualmente válido pero más ceremonioso. Vue es más accesible, tiene mejor curva de aprendizaje y para un proyecto de este tamaño, menos boilerplate. Ambos son excelentes; Vue es la elección correcta si ya te es familiar. |
| **FastAPI + Svelte**               | ✅ Interesante          | Svelte genera código más ligero y reactivo. Pero su ecosistema es menor y la comunidad más reducida. Para un primer proyecto web, Vue ofrece mejor soporte y documentación.                                                           |
| **Node.js (Express/NestJS) + Vue** | ❌ Desaconsejado        | Requiere reescribir toda la lógica de juego en JavaScript/TypeScript. El modelo Python actual es limpio, testado y funcional — no hay razón para descartarlo.                                                                         |

### 2.3 Recomendación final

**FastAPI + Vue es la elección óptima para este caso.** Razones concretas:

1. **FastAPI es async-native**: Tu proyecto ya usa asyncio extensivamente. La migración de sockets TCP a WebSockets de FastAPI es orgánica.
2. **Pydantic reemplaza tus TypedDicts**: Los mensajes del protocolo (`MensajeProtocolo`) se migran directamente a modelos Pydantic con validación automática.
3. **Docs OpenAPI gratis**: FastAPI genera documentación interactiva (Swagger/ReDoc) para tu API de autenticación e historial.
4. **El modelo de juego se reutiliza íntegro**: Barco, Tablero, Partida, PartidaPVE, PartidaPVP → se integran tal cual.
5. **WebSockets nativos**: FastAPI + Starlette manejan WebSockets de forma simple, reemplazando el servidor TCP custom.
6. **Vue es ideal para el frontend**: Estado reactivo para tableros, composables para WebSocket, ligero y con excelente DX.

**Un apunte importante:** para la comunicación PvP en tiempo real, la clave es migrar de **TCP sockets crudos** a **WebSockets**. Esto simplifica enormemente la infraestructura: un solo servidor HTTP/WS gestiona tanto la API REST (auth, historial) como la comunicación de juego (WebSockets).

---

## 3. Decisiones técnicas de diseño

### 3.1 Base de datos

| Opción                      | Recomendación                                     |
| --------------------------- | ------------------------------------------------- |
| **SQLite** (desarrollo)     | ✅ Perfecto para arrancar, sin configuración      |
| **PostgreSQL** (producción) | ✅ Recomendado a largo plazo                      |
| **ORM**                     | SQLAlchemy 2.0 (async) + Alembic para migraciones |

### 3.2 Autenticación

| Opción                    | Recomendación                                          |
| ------------------------- | ------------------------------------------------------ |
| **JWT (JSON Web Tokens)** | ✅ Sin estado, ideal para API + WebSockets             |
| Librería                  | `python-jose` + `passlib[bcrypt]`                      |
| Estrategia                | Access token (corta vida) + Refresh token (larga vida) |

### 3.3 Modelo de datos propuesto

```
┌────────────────┐       ┌─────────────────────┐
│    Usuario     │       │      Partida         │
├────────────────┤       ├─────────────────────┤
│ id (PK)        │       │ id (PK)              │
│ username       │  1──N │ tipo (PVE/PVP)       │
│ email          │◄──────│ jugador1_id (FK)     │
│ password_hash  │◄──────│ jugador2_id (FK|null)│
│ created_at     │       │ ganador_id (FK|null)  │
│ avatar_url     │       │ estado               │
│ elo_rating     │       │ dificultad (PVE)     │
└────────────────┘       │ created_at           │
                         │ finished_at          │
                         │ duracion_segundos    │
                         │ disparos_j1          │
                         │ disparos_j2          │
                         └─────────────────────┘

┌──────────────────────┐
│   EstadisticaUsuario │
├──────────────────────┤
│ usuario_id (FK, PK)  │
│ victorias_pve        │
│ derrotas_pve         │
│ victorias_pvp        │
│ derrotas_pvp         │
│ abandonos            │
│ disparos_totales     │
│ barcos_hundidos      │
│ racha_actual         │
│ mejor_racha          │
└──────────────────────┘
```

### 3.4 Estructura de endpoints API

```
AUTH
  POST   /api/auth/registro          → Crear cuenta
  POST   /api/auth/login             → Obtener tokens JWT
  POST   /api/auth/refresh           → Renovar access token
  POST   /api/auth/logout            → Invalidar refresh token

USUARIO
  GET    /api/usuarios/me            → Perfil del usuario autenticado
  PUT    /api/usuarios/me            → Actualizar perfil
  GET    /api/usuarios/me/estadisticas → Estadísticas del usuario
  GET    /api/usuarios/{id}/perfil   → Perfil público de otro usuario
  GET    /api/usuarios/ranking       → Ranking general (por ELO o victorias)

PARTIDAS
  GET    /api/partidas/historial     → Historial del usuario autenticado
  GET    /api/partidas/{id}          → Detalle de una partida

JUEGO (WebSockets)
  WS     /ws/pve                     → Partida contra la IA
  WS     /ws/pvp                     → Matchmaking + partida PvP
```

---

## 4. Hoja de ruta

### Fase 0: Preparación del entorno (estimación: paso previo)

- [ ] **0.1** Crear rama `feature/web-migration` en Git.
- [ ] **0.2** Definir estructura de carpetas del nuevo proyecto:
  ```
  hundir_la_flota/
  ├── backend/                    # FastAPI
  │   ├── app/
  │   │   ├── main.py             # Punto de entrada FastAPI
  │   │   ├── core/
  │   │   │   ├── config.py       # Settings (Pydantic BaseSettings)
  │   │   │   ├── security.py     # JWT, hashing passwords
  │   │   │   └── database.py     # SQLAlchemy engine, session
  │   │   ├── models/             # Modelos SQLAlchemy (Usuario, Partida)
  │   │   ├── schemas/            # Esquemas Pydantic (request/response)
  │   │   ├── api/
  │   │   │   ├── auth.py         # Endpoints de autenticación
  │   │   │   ├── usuarios.py     # Endpoints de usuarios
  │   │   │   ├── partidas.py     # Endpoints de historial
  │   │   │   └── deps.py         # Dependencias (get_current_user, etc.)
  │   │   ├── ws/
  │   │   │   ├── manager.py      # ConnectionManager para WebSockets
  │   │   │   ├── pve.py          # Endpoint WS para PvE
  │   │   │   └── pvp.py          # Endpoint WS para PvP + matchmaking
  │   │   ├── services/           # Lógica de negocio
  │   │   └── game/               # ← Lógica de juego reutilizada
  │   │       ├── barco.py        # Migrado directamente
  │   │       ├── tablero.py      # Migrado directamente
  │   │       ├── partida.py      # Migrado/adaptado
  │   │       ├── partida_pve.py
  │   │       └── partida_pvp.py
  │   ├── migrations/             # Alembic
  │   ├── tests/
  │   ├── requirements.txt
  │   └── alembic.ini
  │
  ├── frontend/                   # Vue 3
  │   ├── src/
  │   │   ├── views/              # Páginas (Login, Lobby, Game, Profile)
  │   │   ├── components/         # Componentes (Board, Ship, Cell, etc.)
  │   │   ├── composables/        # Lógica reutilizable (useWebSocket, useAuth)
  │   │   ├── stores/             # Pinia (estado global: auth, game)
  │   │   ├── router/             # Vue Router
  │   │   └── api/                # Cliente HTTP (axios/fetch)
  │   ├── package.json
  │   └── vite.config.js
  │
  └── docker-compose.yml          # Opcional: DB + backend + frontend
  ```
- [ ] **0.3** Instalar dependencias base del backend:
  ```
  fastapi uvicorn[standard] sqlalchemy[asyncio] alembic
  aiosqlite asyncpg python-jose[cryptography] passlib[bcrypt]
  pydantic-settings python-multipart
  ```
- [ ] **0.4** Inicializar frontend con Vue 3:
  ```
  npm create vue@latest frontend -- --typescript --router --pinia
  ```

---

### Fase 1: Backend — Base de datos y autenticación

- [ ] **1.1** Configurar SQLAlchemy async + crear `database.py` con engine y `AsyncSession`.
- [ ] **1.2** Definir modelos SQLAlchemy: `Usuario`, `Partida`, `EstadisticaUsuario`.
- [ ] **1.3** Configurar Alembic y generar la migración inicial.
- [ ] **1.4** Implementar `security.py`: funciones de hashing (`passlib`) y JWT (`python-jose`).
- [ ] **1.5** Crear esquemas Pydantic: `UsuarioCreate`, `UsuarioResponse`, `TokenResponse`, `LoginRequest`.
- [ ] **1.6** Implementar endpoints de auth: `POST /registro`, `POST /login`, `POST /refresh`.
- [ ] **1.7** Implementar dependencia `get_current_user` para proteger rutas.
- [ ] **1.8** Tests unitarios para auth (registro, login, token inválido, refresh).

---

### Fase 2: Backend — API de usuarios y estadísticas

- [ ] **2.1** Endpoint `GET /usuarios/me` — devolver perfil del usuario autenticado.
- [ ] **2.2** Endpoint `PUT /usuarios/me` — actualizar perfil (username, avatar).
- [ ] **2.3** Endpoint `GET /usuarios/me/estadisticas` — victorias, derrotas, racha, etc.
- [ ] **2.4** Endpoint `GET /usuarios/{id}/perfil` — perfil público.
- [ ] **2.5** Endpoint `GET /usuarios/ranking` — top jugadores ordenados por ELO o victorias.
- [ ] **2.6** Tests unitarios para todos los endpoints de usuario.

---

### Fase 3: Backend — Migrar lógica de juego

- [ ] **3.1** Copiar `Barco`, `Tablero`, `ResultadoDisparo` a `backend/app/game/` — sin modificaciones.
- [ ] **3.2** Adaptar `PartidaPVE` para funcionar como componente aislado (sin dependencia de consola).
- [ ] **3.3** Adaptar `PartidaPVP` para funcionar sobre WebSockets en vez de sockets TCP.
- [ ] **3.4** Migrar `PartidaService` como servicio del backend.
- [ ] **3.5** Definir mensajes del protocolo WS con modelos Pydantic (reemplazar TypedDicts).
- [ ] **3.6** Tests unitarios para la lógica de juego migrada (reutilizar tests existentes adaptados).

---

### Fase 4: Backend — WebSockets para partidas en tiempo real

- [ ] **4.1** Crear `ConnectionManager` — gestión de conexiones WS activas, por usuario.
- [ ] **4.2** Implementar `WS /ws/pve`:
  - Autenticar por token (query param o primer mensaje).
  - Crear `PartidaPVE` server-side.
  - Ciclo: recibir disparo → procesar → enviar resultado + estado tablero.
  - Al finalizar: registrar resultado en BD.
- [ ] **4.3** Implementar `WS /ws/pvp`:
  - Autenticar por token.
  - Cola de matchmaking (equivalente a `cola_espera` actual).
  - Al emparejar: crear `SesionPVP` (adaptar la existente).
  - Ciclo: fase colocación → fase turnos → fin.
  - Al finalizar: registrar resultado en BD + actualizar estadísticas.
- [ ] **4.4** Gestión de desconexiones y abandonos (equivalente a `jugador_desconectado`).
- [ ] **4.5** Tests de integración para flujo completo WS (conexión → partida → fin).

---

### Fase 5: Backend — Historial de partidas

- [ ] **5.1** Servicio `PartidaDBService` — crear registro en BD al iniciar partida, actualizar al finalizar.
- [ ] **5.2** Endpoint `GET /partidas/historial` — listar partidas del usuario con paginación.
- [ ] **5.3** Endpoint `GET /partidas/{id}` — detalle de partida (jugadores, resultado, duración, disparos).
- [ ] **5.4** Servicio de estadísticas — actualizar `EstadisticaUsuario` tras cada partida.
- [ ] **5.5** Tests.

---

### Fase 6: Frontend — Estructura base y autenticación

- [ ] **6.1** Configurar proyecto Vue 3 + TypeScript + Vite + Vue Router + Pinia.
- [ ] **6.2** Crear store de autenticación (`useAuthStore`): login, registro, logout, gestión de tokens.
- [ ] **6.3** Configurar interceptor HTTP (axios o fetch wrapper) para inyectar JWT automáticamente.
- [ ] **6.4** Crear vistas: `LoginView`, `RegisterView` con formularios.
- [ ] **6.5** Implementar guards de ruta (redirigir a login si no autenticado).
- [ ] **6.6** Layout base: navbar con usuario, navegación principal.

---

### Fase 7: Frontend — Lobby y perfil

- [ ] **7.1** Vista `LobbyView` — botones para iniciar PvE (selección de dificultad) o PvP.
- [ ] **7.2** Vista `ProfileView` — mostrar estadísticas, historial de partidas, avatar.
- [ ] **7.3** Vista `RankingView` — tabla de clasificación.
- [ ] **7.4** Componente `MatchHistory` — lista paginada de partidas con resultado.

---

### Fase 8: Frontend — Interfaz de juego

- [ ] **8.1** Composable `useGameWebSocket` — conectar al WS, enviar/recibir mensajes, gestionar estado.
- [ ] **8.2** Componente `GameBoard` — tablero interactivo (grid NxN, celdas clickeables).
- [ ] **8.3** Componente `ShipPlacement` — arrastrar/rotar barcos sobre el tablero.
- [ ] **8.4** Componente `GameCell` — celda individual con estados visuales (vacía, agua, tocado, hundido, barco propio).
- [ ] **8.5** Componente `GameStatus` — turno actual, disparos, mensajes del servidor.
- [ ] **8.6** Vista `PveGameView`:
  - Conectar WS `/ws/pve`.
  - Selección de dificultad → colocación automática → fase de disparo.
  - Mostrar tablero rival + disparos restantes.
  - Pantalla de resultado (victoria/derrota).
- [ ] **8.7** Vista `PvpGameView`:
  - Conectar WS `/ws/pvp`.
  - Pantalla de espera (matchmaking).
  - Fase de colocación manual de barcos.
  - Fase de turnos (tablero propio + tablero rival).
  - Indicador de turno, resultado de disparos.
  - Pantalla de resultado final.
- [ ] **8.8** Animaciones y feedback visual: disparos al agua, impactos, barcos hundiéndose.

---

### Fase 9: Integración y testing E2E

- [ ] **9.1** Configurar CORS en FastAPI para permitir peticiones del frontend.
- [ ] **9.2** Tests E2E: flujo completo registro → login → PvE → ver historial.
- [ ] **9.3** Tests E2E: flujo completo login → matchmaking PvP → partida → resultado.
- [ ] **9.4** Probar desconexiones, timeouts, tokens expirados.
- [ ] **9.5** Revisión de seguridad: validación de inputs, rate limiting, sanitización.

---

### Fase 10: Pulido y despliegue

- [ ] **10.1** Dockerizar: Dockerfile para backend + frontend + docker-compose con DB.
- [ ] **10.2** Variables de entorno para configuración (SECRET_KEY, DATABASE_URL, etc.).
- [ ] **10.3** Documentación de API (FastAPI la genera automáticamente en `/docs`).
- [ ] **10.4** README actualizado con instrucciones de instalación y ejecución.
- [ ] **10.5** CI/CD básico (GitHub Actions: lint + tests en cada push).

---

## 5. Mapeo de reutilización del código actual

Uno de los mayores activos del proyecto actual es que **la lógica de juego es completamente independiente de la interfaz y la red**. Esto permite una migración eficiente:

| Componente actual               | Destino en el nuevo stack                 | Acción                                     |
| ------------------------------- | ----------------------------------------- | ------------------------------------------ |
| `modelo/barco.py`               | `backend/app/game/barco.py`               | Copiar sin cambios                         |
| `modelo/tablero.py`             | `backend/app/game/tablero.py`             | Copiar sin cambios                         |
| `modelo/resultado.py`           | `backend/app/game/resultado.py`           | Copiar sin cambios                         |
| `modelo/partida/partida.py`     | `backend/app/game/partida.py`             | Copiar sin cambios                         |
| `modelo/partida/partida_pve.py` | `backend/app/game/partida_pve.py`         | Copiar sin cambios                         |
| `modelo/partida/partida_pvp.py` | `backend/app/game/partida_pvp.py`         | Copiar sin cambios                         |
| `servicios/partida_service.py`  | `backend/app/services/partida_service.py` | Adaptar mínimamente                        |
| `config/constantes.py`          | `backend/app/core/game_config.py`         | Copiar, quizás migrar a Pydantic Settings  |
| `red/protocolo/mensajes.py`     | `backend/app/schemas/ws_messages.py`      | Migrar TypedDicts → modelos Pydantic       |
| `red/servidor/sesion_pvp.py`    | `backend/app/ws/pvp.py`                   | Adaptar de TCP a WebSocket                 |
| `red/servidor/servidor.py`      | `backend/app/ws/manager.py`               | Adaptar matchmaking a WS                   |
| `vista/`                        | `frontend/`                               | Reescribir en Vue (la consola se descarta) |
| `controlador/`                  | Se disuelve entre API + WS handlers       | La lógica de controladores se reparte      |
| `tests/unit/modelo/`            | `backend/tests/unit/game/`                | Reutilizar adaptando imports               |
| `tests/unit/red/`               | `backend/tests/unit/ws/`                  | Reescribir para WebSockets                 |

**~60% del código Python se reutiliza directamente o con adaptaciones mínimas.**

---

## 6. Prioridades y dependencias entre fases

```
Fase 0 (Preparación)
  │
  ├──► Fase 1 (Auth + BD)
  │       │
  │       ├──► Fase 2 (API usuarios)
  │       │       │
  │       │       └──► Fase 5 (Historial)
  │       │
  │       └──► Fase 3 (Migrar lógica juego)
  │               │
  │               └──► Fase 4 (WebSockets)
  │                       │
  │                       └──► Fase 5 (Historial) ◄── también depende de Fase 2
  │
  └──► Fase 6 (Frontend base + auth) ◄── puede hacerse en paralelo con Fase 1
          │
          ├──► Fase 7 (Lobby + perfil) ◄── necesita Fases 2, 5
          │
          └──► Fase 8 (Interfaz juego) ◄── necesita Fase 4
                  │
                  └──► Fase 9 (Integración E2E)
                          │
                          └──► Fase 10 (Despliegue)
```

**Se puede paralelizar el trabajo backend (Fases 1-5) con el frontend (Fases 6-8)** si hay disponibilidad para trabajar en ambos simultáneamente, usando mocks en el frontend mientras el backend se desarrolla.

---

## 7. Riesgos y mitigaciones

| Riesgo                                  | Impacto             | Mitigación                                                                                      |
| --------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------- |
| Complejidad de WebSockets en producción | Alto                | Usar `ConnectionManager` robusto, tests de desconexión, heartbeat/ping                          |
| Sincronización de estado en PvP         | Alto                | Mantener la lógica de juego server-side (el servidor es la fuente de verdad)                    |
| Seguridad de WebSockets                 | Medio               | Autenticar en el handshake WS, validar cada mensaje con Pydantic                                |
| Escalabilidad del matchmaking           | Bajo (inicialmente) | El diseño actual (cola en memoria) funciona para cientos de jugadores. Si crece, migrar a Redis |
| Rendimiento de la BD                    | Bajo                | SQLite para desarrollo, PostgreSQL para producción. Índices en las FK                           |

---

## 8. Resumen

El proyecto actual tiene una base sólida con excelente separación de responsabilidades. La migración a **FastAPI + Vue** es la elección correcta porque:

- **FastAPI** es async-native como tu código actual, soporta WebSockets nativamente, genera documentación API automática, y Pydantic valida tus mensajes de protocolo de forma superior a TypedDict.
- **Vue 3** con Composition API ofrece reactividad ideal para renderizar tableros en tiempo real, composables para gestión de WebSocket, y es ligero y accesible.
- **~60% del código Python se reutiliza** directamente, especialmente toda la lógica de juego.
- La mayor parte del trabajo nuevo es: base de datos + auth + frontend + adaptación de sockets TCP a WebSockets.

La hoja de ruta define **10 fases concretas** con tareas específicas, dependencias claras entre fases, y oportunidades de paralelización entre backend y frontend.
