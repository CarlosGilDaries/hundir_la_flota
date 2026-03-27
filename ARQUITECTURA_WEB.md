# 🎯 Análisis y Hoja de Ruta: Migración a Aplicación Web

**Fecha:** Marzo 2026  
**Proyecto:** Hundir la Flota – Escalabilidad a Plataforma Web  
**Objetivo:** Migrar de aplicación CLI a plataforma web con base de datos, autenticación y API REST

---

## 📋 Tabla de Contenidos

1. [Análisis de Opciones](#análisis-de-opciones)
2. [Recomendación Profesional](#recomendación-profesional)
3. [Estrategia de Arquitectura](#estrategia-de-arquitectura)
4. [Hoja de Ruta Detallada](#hoja-de-ruta-detallada)
5. [Migración Incremental](#migración-incremental)

---

## 📊 Análisis de Opciones

### 1. Django

**¿Qué es?** Framework web de pila completa (full-stack) muy popular en empresas.

#### Ventajas ✅
- **ORM integrado** (Django ORM) potente y bien documentado
- **Admin panel automático** para gestión de datos (sin código)
- **Comunidad enorme** con abundantes recursos y librerías
- **Seguridad robusta** (CSRF, SQL injection, etc. preconfigurados)
- **MVT integrado** (Model-View-Template) similar a tu actual MVC
- **Excelente para aprender** en contexto empresarial
- **Migraciones automáticas** de base de datos

#### Desventajas ⚠️
- **No es async-nativo** (Django usa threads/WSGI, aunque Django 4.1+ tiene soporte partial)
- **Overhead significativo** para aplicaciones pequeñas/medianas
- **API Rest requiere DRF** (Django REST Framework - otra dependencia)
- **Menos flexible** que microframeworks (opiniones opuestas)
- **Conflicto potencial** con tu código asyncio existente en PVP
- **Curva de aprendizaje pronunciada** (muchos conceptos)

#### Caso de Uso Ideal
Empresas grandes, proyectos monolíticos, equipos numerosos.

---

### 2. **FastAPI** ⭐ (RECOMENDADO)

**¿Qué es?** Microframework moderno y asincrónico para APIs REST.

#### Ventajas ✅
- **Async-nativo** ⭐ (integración perfecta con `asyncio` existente)
- **Validación automática** (Pydantic) - tipo-safe desde inicio
- **Documentación interactiva automática** (Swagger/OpenAPI)
- **Rendimiento excelente** (comparable a Go, Node.js)
- **Menor curva de aprendizaje** que Django
- **Ideal para APIs modernas** (REST, WebSockets)
- **Flexible y modular** - solo añades lo que necesitas
- **Debugging más sencillo**

#### Desventajas ⚠️
- **Comunidad más pequeña** que Django (pero creciente)
- **Admin panel NO incluido** (se puede integrar Sqladmin)
- **Menos "baterías incluidas"** que Django
- **Requiere conocer SQLAlchemy** (para ORM)
- **Documentación menos exhaustiva** (aunque muy buena)

#### Caso de Uso Ideal
Aplicaciones modernas, startups, APIs escalables, sistemas concurrentes.

---

### 3. Flask

**¿Qué es?** Microframework minimalista.

#### Ventajas ✅
- Muy ligero y flexible
- Curva de aprendizaje suave
- Excelente para prototipos

#### Desventajas ⚠️
- Más boilerplate que FastAPI
- No es async-nativo (requiere extensiones)
- Menos tipo-safe
- Comunidad fragmentada con múltiples extensiones

#### Veredicto ❌
No recomendado para este caso - inferior a FastAPI en prácticamente todo.

---

### 4. Quart (Flask Async)

**¿Qué es?** Versión asincrónica de Flask.

#### Ventajas ✅
- Familiar si conoces Flask
- Async-nativo

#### Desventajas ⚠️
- Comunidad mucho más pequeña
- Menos maduro que FastAPI
- Documentación insuficiente
- Menos adopción empresarial

#### Veredicto ⚠️
Opción válida pero inferior a FastAPI.

---

## 🎯 Recomendación Profesional

### 🏆 **FastAPI es la mejor opción para este proyecto**

#### Justificación:

1. **Compatibilidad con código existente**
   - Tu aplicación usa `asyncio` extensivamente
   - FastAPI es async-nativo, Django no
   - **Reutilizarás la lógica de servidor PVP sin refactorizar**

2. **Modernidad tecnológica**
   - FastAPI representa el futuro de Python web
   - Mejor perspectiva laboral (startups tech, scale-ups)
   - Mejor para sistemas con alta concurrencia

3. **Escalabilidad**
   - Tu sistema PVP necesita WebSockets y conexiones simultáneas
   - FastAPI maneja esto nativamente
   - Django requeriría Django Channels (complejidad añadida)

4. **Curva de aprendizaje**
   - Más suave que Django
   - Conceptos claros y directos
   - Documentación excelente

5. **Flexibilidad arquitectónica**
   - Tus modelos de negocio (Barco, Tablero, Partida) reutilizables
   - Separación clara: logica negocio ↔ API ↔ BD

### ⚠️ Posibilidad: Django como alternativa

**Si prefieres Django por razones empresariales:**
- ✅ Viable, pero requiere Django Channels para async/WebSockets
- ✅ Mejor para equipos grandes
- ✅ Comunidad y empleabilidad muy alta
- ⚠️ Requiere refactorización mayor del código PVP existente

**Recomendación:** Comienza con FastAPI. Si posteriormente necesitas admin panel, puedes integrar Sqladmin o migrarte a Django.

---

## 🏗️ Estrategia de Arquitectura

### Estructura Propuesta

```
hundir-la-flota-web/
├── backend/                          # Aplicación FastAPI
│   ├── app/
│   │   ├── main.py                   # Punto entrada FastAPI
│   │   ├── config.py                 # Configuración
│   │   └── requirements.txt
│   ├── app/api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py           # Endpoints autenticación
│   │   │   │   ├── users.py          # Endpoints usuarios
│   │   │   │   ├── games.py          # Endpoints partidas
│   │   │   │   ├── stats.py          # Endpoints estadísticas
│   │   │   │   └── leaderboard.py   # Endpoints ranking
│   │   │   └── dependencies.py       # Dependencias inyectables
│   ├── app/db/
│   │   ├── __init__.py
│   │   ├── models.py                 # Modelos SQLAlchemy
│   │   └── schemas.py                # Esquemas Pydantic
│   ├── app/servicios/                # REUSAR lógica negocio
│   │   ├── juego/                    # (Importar desde proyecto original)
│   │   │   ├── barco.py
│   │   │   ├── tablero.py
│   │   │   └── partida/
│   │   ├── auth.py                   # Servicios autenticación
│   │   └── stats.py                  # Servicios estadísticas
│   ├── app/red/                      # REUSAR servidor PVP
│   │   ├── servidor_pvp.py           # (Refactorudo mínimamente)
│   │   └── websockets.py             # WebSocket handlers
│   ├── app/utils/                    # REUSAR utilidades
│   │   ├── excepciones.py
│   │   ├── log.py
│   │   └── validators.py
│   └── tests/                        # Tests API y modelos
│
├── frontend/                         # Aplicación web (Vue/React)
│   ├── src/
│   │   ├── components/               # Componentes reutilizables
│   │   ├── views/                    # Vistas principales
│   │   ├── api/                      # Cliente HTTP a FastAPI
│   │   ├── websocket.js              # Cliente WebSocket
│   │   └── store/                    # Estado (Pinia/Vuex/Redux)
│   └── public/
│
└── docker-compose.yml                # PostgreSQL, Redis, Backend, Frontend
```

### Reutilización de Código Existente

| Módulo Actual | Destino Web | Cambios |
|---|---|---|
| `modelo/barco.py` | `backend/app/servicios/juego/barco.py` | ✅ Sin cambios |
| `modelo/tablero.py` | `backend/app/servicios/juego/tablero.py` | ✅ Sin cambios |
| `modelo/partida/` | `backend/app/servicios/juego/partida/` | ✅ Sin cambios |
| `red/servidor/` | `backend/app/red/servidor_pvp.py` | ⚠️ Refactorizar para FastAPI |
| `utils/` | `backend/app/utils/` | ✅ Sin cambios |
| `servicios/` | `backend/app/servicios/` | ✅ Sin cambios |

**Estimación:** 60-70% del código puede reutilizarse directamente.

---

## 🗺️ Hoja de Ruta Detallada

### Fase 1: Preparación (Semana 1-2)

#### 1.1 Configuración del Entorno Backend
```bash
# Crear estructura de proyecto
mkdir hundir-la-flota-web/backend
cd hundir-la-flota-web/backend

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install fastapi uvicorn
pip install sqlalchemy alembic
pip install pydantic pydantic-settings
pip install python-dotenv
pip install passlib[bcrypt] python-jose[cryptography]
pip install pytest pytest-asyncio
pip install psycopg2-binary  # PostgreSQL
```

#### 1.2 Instalar Base de Datos
```bash
# Opción recomendada: PostgreSQL
# Descargar desde: https://www.postgresql.org/download/
# O usar Docker: docker run -d --name postgres -e POSTGRES_PASSWORD=pwd postgres

# Alternativa: SQLite (desarrollo rápido)
# No requiere instalación
```

#### 1.3 Crear Estructura Base FastAPI
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hundir la Flota API",
    description="API para juego multijugador",
    version="1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: específicas
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Tareas:**
- [ ] Crear estructura de directorios
- [ ] Instalar dependencias FastAPI
- [ ] Configurar PostgreSQL o SQLite
- [ ] Crear app base FastAPI
- [ ] Verificar que `/api/v1/health` funciona

---

### Fase 2: Modelos de Base de Datos (Semana 2-3)

#### 2.1 Crear Modelos SQLAlchemy

```python
# backend/app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True)
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"))
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    game_type = Column(Enum("PVE", "PVP"), default="PVP")
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class GameResult(Base):
    __tablename__ = "game_results"
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("users.id"))
    result = Column(Enum("WIN", "LOSS", "DRAW"), default="LOSS")
    ships_destroyed = Column(Integer)
    shots_fired = Column(Integer)
    accuracy = Column(Integer)  # Porcentaje
```

#### 2.2 Crear Esquemas Pydantic

```python
# backend/app/db/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

class GameCreate(BaseModel):
    player1_id: int
    player2_id: int
    game_type: str

class GameResultResponse(BaseModel):
    game_id: int
    player_id: int
    result: str
    ships_destroyed: int
    shots_fired: int
    accuracy: int
```

#### 2.3 Configurar Alembic (Migraciones)

```bash
# Inicializar Alembic
alembic init alembic

# Crear primera migración
alembic revision --autogenerate -m "Initial schema"

# Aplicar migración
alembic upgrade head
```

**Tareas:**
- [ ] Diseñar y crear modelos SQLAlchemy (User, Game, GameResult, etc.)
- [ ] Crear esquemas Pydantic correspondientes
- [ ] Configurar Alembic
- [ ] Crear primera migración
- [ ] Verificar que migrations se aplican correctamente

---

### Fase 3: API de Autenticación (Semana 3-4)

#### 3.1 Implementar JWT y Hash de Contraseñas

```python
# backend/app/servicios/auth.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = "tu-clave-secretissima"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### 3.2 Endpoints de Autenticación

```python
# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.models import User
from app.db.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar que no existe
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username taken")
    
    # Crear usuario
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```

**Tareas:**
- [ ] Implementar funciones de hash de contraseña (bcrypt)
- [ ] Crear sistema JWT
- [ ] Implementar endpoints `/register` y `/login`
- [ ] Crear middleware de autenticación
- [ ] Probar autenticación en Swagger UI

---

### Fase 4: API de Partidas y Estadísticas (Semana 4-5)

#### 4.1 Endpoints de Partidas

```python
# backend/app/api/v1/endpoints/games.py
@router.get("/api/v1/games/history")
async def get_game_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    games = db.query(Game).filter(
        (Game.player1_id == current_user.id) | (Game.player2_id == current_user.id)
    ).order_by(Game.created_at.desc()).all()
    return games

@router.post("/api/v1/games/start")
async def start_game(game: GameCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Crear registro de partida
    new_game = Game(
        player1_id=current_user.id,
        player2_id=game.player2_id,
        game_type=game.game_type
    )
    db.add(new_game)
    db.commit()
    return {"game_id": new_game.id}

@router.post("/api/v1/games/{game_id}/result")
async def save_game_result(game_id: int, result: GameResultResponse, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Guardar resultado
    result_record = GameResult(
        game_id=game_id,
        player_id=current_user.id,
        result=result.result,
        ships_destroyed=result.ships_destroyed,
        shots_fired=result.shots_fired,
        accuracy=result.accuracy
    )
    db.add(result_record)
    db.commit()
    return result_record
```

#### 4.2 Endpoints de Estadísticas y Ranking

```python
# backend/app/api/v1/endpoints/stats.py
@router.get("/api/v1/stats/{user_id}")
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    # Calcular estadísticas del usuario
    results = db.query(GameResult).filter(GameResult.player_id == user_id).all()
    
    total_games = len(results)
    wins = len([r for r in results if r.result == "WIN"])
    accuracy = sum(r.accuracy for r in results) / total_games if total_games > 0 else 0
    
    return {
        "total_games": total_games,
        "wins": wins,
        "losses": total_games - wins,
        "win_rate": (wins / total_games * 100) if total_games > 0 else 0,
        "average_accuracy": accuracy
    }

@router.get("/api/v1/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db), limit: int = 10):
    # Top 10 jugadores por victorias
    leaders = db.query(User, func.count(GameResult.id)).join(
        GameResult, GameResult.player_id == User.id, GameResult.result == "WIN"
    ).group_by(User.id).order_by(func.count(GameResult.id).desc()).limit(limit).all()
    
    return leaders
```

**Tareas:**
- [ ] Crear endpoints CRUD de partidas
- [ ] Implementar system de guardado de resultados
- [ ] Crear endpoints de estadísticas de usuario
- [ ] Implementar leaderboard global
- [ ] Probar endpoints en Swagger UI

---

### Fase 5: WebSockets para PVP (Semana 5-6)

#### 5.1 Integrar Servidor PVP Existente

**Reutilizar `red/servidor/sesion_pvp.py` con mínimos cambios:**

```python
# backend/app/red/websockets.py
from fastapi import WebSocket
from app.red.sesion_pvp import SesionPVP  # Importar existente
from app.servicios.juego import Barco, Tablero  # Reutilizar

class GameConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.waiting_players = []
        self.active_games = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.waiting_players.append(user_id)
        
        # Si hay 2 jugadores, iniciar partida
        if len(self.waiting_players) >= 2:
            player1, player2 = self.waiting_players[:2]
            game = SesionPVP(player1, player2)  # Reutilizar clase
            await self.start_game(game)

manager = GameConnectionManager()

@app.websocket("/api/v1/ws/game/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Procesar movimiento
            result = await process_shot(data)
            await manager.broadcast(result)
    except Exception as e:
        await manager.disconnect(user_id)
```

**Tareas:**
- [ ] Refactorizar `sesion_pvp.py` para uso con FastAPI
- [ ] Crear `GameConnectionManager`
- [ ] Implementar WebSocket endpoint
- [ ] Integrar lógica de juego existente (`Tablero`, `Barco`, `Partida`)
- [ ] Probar en cliente WebSocket

---

### Fase 6: Frontend Web (Semana 6-8)

Opciones recomendadas:

- **Vue 3** (más fácil, muy intuitivo)
- **React** (más demanda laboral, ecosistema enorme)

#### 6.1 Estructura Vue 3 (Ejemplo)

```javascript
// frontend/src/api/auth.js
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export const authAPI = {
  async register(username, email, password) {
    const response = await axios.post(`${API_BASE}/auth/register`, {
      username, email, password
    })
    localStorage.setItem('token', response.data.access_token)
    return response.data
  },
  
  async login(username, password) {
    const response = await axios.post(`${API_BASE}/auth/login`, {
      username, password
    })
    localStorage.setItem('token', response.data.access_token)
    return response.data
  }
}
```

```vue
<!-- frontend/src/views/GameBoard.vue -->
<template>
  <div class="game-container">
    <div class="my-board" v-for="cell in myBoard" :key="cell.id">
      <div class="cell" :class="cell.status"></div>
    </div>
    <div class="opponent-board" @click="fireShot">
      <div class="cell" v-for="cell in opponentBoard" :key="cell.id"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'

const myBoard = ref([])
const opponentBoard = ref([])
const { send, on } = useWebSocket('/api/v1/ws/game')

onMounted(() => {
  on('game_start', (data) => {
    myBoard.value = data.my_board
    opponentBoard.value = data.opponent_board
  })
})

const fireShot = async (x, y) => {
  send({ action: 'shot', x, y })
}
</script>
```

**Tareas:**
- [ ] Escoller framework (Vue 3 o React)
- [ ] Crear layout principal
- [ ] Implementar vistas:
  - Login/Register
  - Tablero de juego
  - Historial de partidas
  - Leaderboard
- [ ] Integrar con API FastAPI
- [ ] Crear cliente WebSocket para PVP
- [ ] Testing y optimización

---

### Fase 7: Despliegue y Containerización (Semana 8-9)

#### 7.1 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secretpassword
      POSTGRES_DB: hundir_la_flota
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:secretpassword@postgres:5432/hundir_la_flota
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

**Tareas:**
- [ ] Crear Dockerfiles para backend y frontend
- [ ] Crear `docker-compose.yml`
- [ ] Probar con Docker Compose
- [ ] Documentar despliegue en producción (AWS, Vercel, etc.)

---

## 🔄 Migración Incremental (IMPORTANTE)

### Enfoque Recomendado: NO hacer "big bang"

**En lugar de:**
❌ Reescribir todo de una vez

**Hacer:**
✅ Mantener aplicación CLI original mientras se desarrolla web

### Pasos:

1. **Semanas 1-2:** Iniciar backend FastAPI en paralelo. Aplicación CLI sigue funcionando.
2. **Semanas 2-4:** Desarrollar API de autenticación y base de datos.
3. **Semana 4-5:** Crear endpoints de partidas (sin reemplazar CLI aún).
4. **Semana 5-6:** Implementar WebSockets, refactorizar código existente.
5. **Semana 6-8:** Desarrollar frontend en paralelo.
6. **Semana 8-9:** Migración final: redirigir tráfico a web, deprecar CLI.

### Ventajas:
- ✅ Reducir riesgo
- ✅ Testing gradual
- ✅ Poder revertir si hay problemas
- ✅ Usuarios pueden usar versión antigua mientras se desarrolla nueva

---

## 📚 Recursos y Documentación

### FastAPI
- Documentación oficial: https://fastapi.tiangolo.com/
- Tutoriales recomendados: https://fastapi.tiangolo.com/tutorial/
- WebSockets: https://fastapi.tiangolo.com/advanced/websockets/

### SQLAlchemy
- Documentación: https://docs.sqlalchemy.org/
- ORM Tutorial: https://docs.sqlalchemy.org/en/20/orm/

### PostgreSQL
- Instalación: https://www.postgresql.org/download/
- Documentación: https://www.postgresql.org/docs/

### Frontend
- **Vue 3:** https://vuejs.org/
- **React:** https://react.dev/
- **WebSockets en JS:** https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

### Despliegue
- Docker: https://docs.docker.com/
- Heroku: https://devcenter.heroku.com/
- AWS: https://aws.amazon.com/
- Vercel (Frontend): https://vercel.com/

---

## ✅ Checklist Final

### Antes de comenzar:
- [ ] Entender arquitectura de FastAPI vs Django
- [ ] Aprender conceptualización de Pydantic
- [ ] Aprender manejo de async/await en Python
- [ ] Familiarizarse con SQLAlchemy

### Fase 1-2:
- [ ] Entorno preparado
- [ ] BD instalada y conectada
- [ ] Estructura FastAPI funcionando
- [ ] Modelos y esquemas diseñados

### Fase 3-4:
- [ ] API de autenticación testeada
- [ ] API de partidas funcionando
- [ ] Endpoints de estadísticas operativos

### Fase 5-6:
- [ ] WebSockets integrados con lógica existente
- [ ] Frontend conectando a API
- [ ] Juego funcionando en navegador

### Fase 7:
- [ ] Containerizado con Docker
- [ ] Documentación completada
- [ ] Despliegue en servidor

---

## 🎓 Aprendizaje Adicional

### Conceptos clave a dominar durante el desarrollo:

1. **Async/Await avanzado:** Profundizar más allá de lo básico
2. **Inyección de dependencias:** Patrón clave en FastAPI
3. **Middleware:** Para logging, autenticación, etc.
4. **Testing de APIs:** pytest con FastAPI
5. **Pattern WebSockets:** Para comunicación real-time
6. **Optimización de BD:** Índices, queries, N+1 problems
7. **Seguridad:** CORS, CSRF, rate limiting, SQL injection
8. **CI/CD:** GitHub Actions para testing automático

---

## 📞 Conclusión

**FastAPI es tu mejor aliado** para modernizar esta aplicación. Te permite:

✅ Reutilizar código existente  
✅ Aprender tecnología moderna  
✅ Escalar fácilmente  
✅ Mantener async-first  
✅ Mejor perspectiva laboral  

**Tiempo estimado:** 8-9 semanas con dedic ación part-time (20 horas/semana)

**Resultado final:** Una plataforma web profesional, escalable y moderna.

---

*Documento generado: Marzo 2026*
*Proyecto: Hundir la Flota – Escalabilidad Web*
