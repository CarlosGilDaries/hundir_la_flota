app/
   app.py
   partida_service.py

config/
    constantes.py
    mensajes.py
    protocolo.py

modelo/
    partida/                    # 📁 Nuevo directorio
        __init__.py
        partida.py              # Clase abstracta/base
        partida_pve.py          # Implementación PVE
        partida_pvp.py          # Implementación PVP
    barco.py
    tablero.py
    resultado.py

controlador/
    controlador.py              # Clase abstracta/base
    controlador_pve.py
    controlador_pvp_cliente.py

red/
    servidor.py
    sesion_pvp.py
    globales.py

vista/
    vista_base.py
    consola/
        __init__.py
        vista_consola.py    # Clase abstracta

utils/
    __init__.py
    validador.py
    excepciones.py

main.py