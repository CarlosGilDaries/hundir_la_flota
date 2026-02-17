# Hundir la Flota - Versión 3.0

**Hundir la Flota** es un juego de estrategia tipo "batalla naval" desarrollado en **Python 3.13.2**.  
El jugador debe hundir todos los barcos del tablero haciendo disparos coordinados. 
Esta versión 3.0 incluye mejoras en la organización del código, modularidad, una interfaz de consola clara y disitintas dificultades.

---

## Características del juego

- Juego por consola con visualización del tablero y sus coordenadas.
- Barcos generados aleatoriamente según la dificultad seleccionada.
- Comprobación de disparos repetidos y aciertos.
- Sistema de disparos limitados según la dificultad.
- Mensajes interactivos para aciertos, hundimientos, errores y fin de partida.
- Código modular con clases principales:
  - `Barco`  
  - `Tablero`  
  - `Juego`  
  - `InterfazConsola`  
  - `Menu`  
  - `App` (gestiona el flujo principal)
- Validación de entradas de usuario mediante la clase `Util`.

---

## Requisitos

- Python **3.13.2**
- No requiere librerías externas, solo módulos estándar (`random`, `os`).

---

## Instalación y ejecución

1. Clonar el repositorio:

```bash
git clone https://github.com/charlygilpsi/hundir_la_flota.git
cd hundir_la_flota
```

2. Ejecutar el juego:

```bash
python main.py
```

---

## Estrucutra del proyecto

```text
hundir_la_flota/
│
├─ main.py                  # Punto de entrada del juego
├─ app/
│   └─ app.py               # Clase App que gestiona el flujo principal
├─ dominio/
│   ├─ barco.py             # Clase Barco
│   ├─ tablero.py           # Clase Tablero
│   └─ juego.py             # Clase Juego
├─ vista/
│   └─ consola/
│       ├─ interfaz_consola.py   # Interfaz de usuario por consola
│       └─ menu_consola.py       # Menú principal y de dificultad
├─ utils/
│   ├─ excepciones.py        # Excepciones personalizadas
│   └─ utils.py             # Funciones de validación
└─ config/
    ├─ constantes.py        # Parámetros de configuración (tablero, caracteres)
    └─ mensajes.py          # Textos e instrucciones del juego
```
