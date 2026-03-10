# 🚢 Hundir la Flota (Battleship) – Python Async MVC

![Python](https://img.shields.io/badge/Python-3.13.2-blue)
![asyncio](https://img.shields.io/badge/Async-asyncio-green)
![Architecture](https://img.shields.io/badge/Architecture-MVC-orange)
![Principles](https://img.shields.io/badge/Principles-SOLID-yellow)
![Network](https://img.shields.io/badge/Network-TCP%2FJSON-blueviolet)

Implementación del clásico juego **Hundir la Flota** desarrollada en **Python 3.13.2**, diseñada como ejercicio práctico para mejorar competencias avanzadas en: Programación Orientada a Objetos (POO), Principios **SOLID**, Arquitectura **MVC**, Programación **asíncrona con `asyncio`** y Diseño modular y escalable.

El proyecto incluye tanto **modo local (PVE)** como **modo multijugador por red (PVP)**, permitiendo partidas simultáneas entre jugadores mediante un servidor asíncrono.

---

## 🎯 Objetivos del proyecto

El objetivo principal del proyecto fue **mejorar la competencia en Python** aplicando buenas prácticas de arquitectura y diseño de software.

Durante el desarrollo se buscó:

- Aplicar **principios SOLID** en la estructura del código
- Diseñar un sistema basado en **Programación Orientada a Objetos**
- Implementar una arquitectura **MVC (Model–View–Controller)**
- Desarrollar una aplicación modular y mantenible
- Implementar comunicación **cliente-servidor**
- Utilizar **asincronía con `asyncio`** para gestionar múltiples conexiones

El diseño del proyecto se planteó desde el inicio con una intención clara:

> Construir una arquitectura que permitiera implementar primero el juego en consola y posteriormente facilitar su migración a una **interfaz web** sin modificar la lógica de negocio.

---

## 🏗️ Arquitectura

El proyecto utiliza una arquitectura **MVC (Model – View – Controller)** para separar responsabilidades y facilitar la escalabilidad.

### Model

Contiene la lógica de negocio del juego:

- Tablero
- Barcos
- Resultado de disparos
- Gestión de partidas

### View

Gestiona exclusivamente la **interacción con el usuario**.

Actualmente está implementada en **consola**, pero está desacoplada del resto del sistema para permitir futuras interfaces (por ejemplo web).

### Controller

Coordina la interacción entre **modelo y vista**, gestionando el flujo del juego.

Existen dos controladores principales:

- `ControladorPVE` → gestiona partidas contra la máquina
- `ControladorPVPCliente` → gestiona partidas multijugador conectadas al servidor

---

## 📚 Documentación del código

El código del proyecto está **completamente documentado utilizando `pydoc`**, incluyendo:

- Descripción de clases y responsabilidades
- Documentación de métodos
- Tipado estático de parámetros
- Tipos de retorno explícitos

Esto facilita:

- La comprensión de la arquitectura del proyecto
- El mantenimiento del código
- La detección temprana de errores mediante herramientas de análisis estático
- La futura extensión del sistema

Además, el protocolo de comunicación cliente-servidor está **tipado mediante `TypedDict`**, permitiendo trabajar con mensajes JSON estructurados y mejorando el autocompletado y la seguridad del código.

---

## 🌐 Networking y concurrencia

Inicialmente se planteó una arquitectura basada en **crear un hilo por jugador o por partida**.

Sin embargo, este enfoque se descartó debido a:

- Alto consumo de memoria
- Mayor complejidad en la gestión de hilos
- Escalabilidad limitada

En su lugar se optó por implementar un **servidor asíncrono utilizando `asyncio`**, lo que permite:

- Gestionar múltiples conexiones simultáneamente
- Reducir el consumo de memoria
- Evitar bloqueos por operaciones de red
- Mejorar la eficiencia del servidor

El servidor gestiona:

- Conexiones de clientes
- Cola de jugadores en espera
- Creación automática de partidas cuando hay dos jugadores disponibles
- Sincronización de turnos entre clientes
- Gestión de desconexiones

La comunicación entre cliente y servidor se realiza mediante **mensajes JSON sobre sockets TCP**.

---

## 🎮 Funcionalidades actuales

La versión actual del proyecto permite:

### Modo PVE

- Partidas contra la máquina
- Diferentes niveles de dificultad

### Modo PVP

- Servidor multijugador basado en `asyncio`
- Emparejamiento automático de jugadores
- Múltiples partidas simultáneas
- Gestión de desconexiones de clientes
- Comunicación cliente-servidor mediante protocolo JSON

---

## 📝 Logging del servidor

Toda la actividad del servidor queda registrada en:

`logs/servidor_log.log`

Incluyendo eventos como:

- Conexiones de clientes
- Creación de partidas
- Disparos y resultados
- Cambios de turno
- Finalización de partidas
- Desconexiones

---

## 📂 Estructura del proyecto

```text
hundir_la_flota/
├── main.py                          # Punto de entrada del cliente
├── app/
│   └── app.py                       # Orquestador principal
├── config/
│   ├── constantes.py                 # Constantes de configuración
│   └── textos.py                     # Textos e instrucciones
├── controlador/
│   ├── controlador.py                 # Clase abstracta base
│   ├── controlador_pve.py              # Controlador para partidas PVE
│   └── controlador_pvp_cliente.py      # Controlador para partidas PVP
├── modelo/
│   ├── barco.py
│   ├── resultado.py
│   ├── tablero.py
│   └── partida/
│       ├── partida.py                  # Clase abstracta
│       ├── partida_pve.py               # Implementación PVE
│       └── partida_pvp.py               # Implementación PVP
├── red/
│   ├── cliente/
│   │   └── cliente_socket.py
│   ├── helpers/
│   │   └── enviar.py
│   ├── protocolo/
│   │   └── mensajes.py
│   └── servidor/
│       ├── servidor.py                  # Servidor asíncrono
│       ├── sesion_pvp.py                 # Gestión de partidas
│       └── servidor_log.log              # Logs del servidor
├── servicios/
│   └── partida_service.py                # Fachada para el modelo
├── utils/
│   ├── excepciones.py
│   ├── log.py
│   ├── log_decorador.py
│   └── utils.py
└── vista/
    ├── vista.py                          # Clase abstracta
    └── consola/
        ├── menu_consola.py
        └── vista_consola.py
```

---

## ▶️ Flujo de ejecución

El sistema se divide en **cliente y servidor**.

### Servidor

El servidor gestiona:

- conexiones entrantes
- cola de jugadores
- creación de sesiones PvP
- sincronización entre clientes

Para iniciar el servidor:

```bash
python -m red.servidor.servidor
```

### Cliente

1. Jugar contra la Máquina (PVE)
2. Jugar contra otro Jugador (PVP)
3. Instrucciones
4. Salir

Para ejecutar el cliente:

```bash
python -m main
```

### Comportamiento según la opción seleccionada

#### Opción 1 – PVE

- Se inicia una partida local contra la máquina  
- No requiere conexión con el servidor  

#### Opción 2 – PVP

- El cliente se conecta al servidor  
- Entra en una cola de emparejamiento  
- Cuando hay dos jugadores disponibles se crea una partida automáticamente

Si el servidor se ejecuta en otro equipo dentro de la misma red local, es necesario modificar la dirección IP del servidor en el cliente.

En el archivo:

`app/app.py`

método:

`async def _ejecutar_pvp(self):`

actualizar la IP del equipo que ejecuta el servidor, por ejemplo:

```bash
cliente = ClienteSocket("192.168.1.35", 8888)
```

---

## 🧰 Tecnologías utilizadas

- **Python 3.13.2**
- **asyncio**
- Programación Orientada a Objetos
- Arquitectura **MVC**
- Principios **SOLID**
- **Sockets TCP**
- Comunicación **JSON cliente-servidor**
- **Logging estructurado**

---

## 🚀 Posibles mejoras futuras

La arquitectura del proyecto permite incorporar nuevas funcionalidades con relativa facilidad:

- Interfaz web
- Sistema de ranking de jugadores
- Matchmaking avanzado
- Persistencia de partidas
- Estadísticas de jugadores
- Espectadores de partidas
- Replays de partidas

---
