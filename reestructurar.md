app/
   app.py

config/
    __init__.py
    constantes.py               # Constantes de configuración, dificultad y caracteres
    textos.py                   # Textos, instrucciones y traducción de enum a str

controlador/
    __init__.py
    controlador.py              # Clase abstracta/base
    controlador_pve.py          # Controlador para partidas pve
    controlador_pvp_cliente.py  # Controlador para partidas pvp

modelo/
    partida/
        __init__.py
        partida.py              # Clase abstracta/base
        partida_pve.py          # Implementación PVE
        partida_pvp.py          # Implementación PVP
    __init__.py
    barco.py
    tablero.py
    resultado.py

red/
    cliente/
        __init__.py
        cliente_socket.py
    helpers/
        __initi__.py
        enviar.py
    protocolo/
        __init__.py
    mensajes.py
    servidor/
        __init__.py
        servidor_log.log
        servidor.py
        sesion_pvp.py

servicios/
    __init__.py
    partida_service.py

utils/
    __init__.py
    excepciones.py
    log_decorador.py
    log.py
    utils.py

vista/
    vista.py    # Clase abstracta
    consola/
        __init__.py
        menu_consola.py
        vista_consola.py

main.py
