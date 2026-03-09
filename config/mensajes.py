"""
Textos del juego Hundir la Flota.
Centraliza todos los mensajes mostrados al usuario.
"""

TEXTOS = {
    "TEXTO_TURNO": "TURNO DEL JUGADOR {}",
    
    # Inputs
    "TEXTO_POSICION_X": "Introduzca la coordenada x: ",
    "TEXTO_POSICION_Y": "Introduzca la coordenada y: ",
    "PULSAR_ENTER" : "\nPulsa Enter para continuar...",

    # Disparos
    "TEXTO_TOCADO_Y_HUNDIDO": "TOCADO Y HUNDIDO",
    "TEXTO_TOCADO": "TOCADO",
    "TEXTO_AGUA": "AGUA",
    "TEXTO_REPETIDO": "YA HABÍAS DISPARADO EN ESTE HUECO. NO PIERDES LA BALA.",
    "TEXTO_BALAS_RESTANTES": "BALAS RESTANTES: ",

    # Final
    "TEXTO_VICTORIA": "TE HAS CARGADO TODOS LOS BARCOS, ENHORABUENA.",
    "TEXTO_DERROTA": "LÁSTIMA, TE HAS QUEDADO SIN BALAS. AFINA TU PUNTERÍA Y VUELVE A INTENTARLO.",
    
    # Terminar programa
    "TEXTO_FIN_JUEGO" : "Escriba 'Salir' para volver al menú.",
    "FIN_DE_PROGRAMA" : "FIN DE PROGRAMA",

    # Errores
    "ERROR_LIMITE_TABLERO": "ERROR: La posición del disparo excede los límites del tablero",
    "ERROR_NUMERO_ENTERO": "ERROR: Introduce números enteros, por favor",
    "ERROR_MENU" : "ERROR: Opción inválida",
}

RED = {
    # Cliente -> Servidor
    "BUSCAR_PARTIDA" : "buscar_partida",
    "CANCELAR_BUSQUEDA" : "cancelar_busqueda",
    "REALIZAR_DISPARO" : "realizar_disparo",
    "ABANDONAR" : "abandonar",
    
    # Servidor -> Cliente
    "ESPERANDO_OPONENTE" : "esperando_oponente",
    "PARTIDA_INICIADA" : "partida_iniciada",
    "TU_TURNO" : "tu_turno",
    "RESULTADO_DISPARO" : "resultado_disparo",
    "VICTORIA" : "victoria",
    "DERROTA" : "derrota",
    "OPONENTE_ABANDONO" : "oponente_abandono",
    "ERROR" : "error"
}

# Instrucciones
INSTRUCCIONES = """
FÁCIL
-------
- Tablero 8x8.
- 60 disparos.
- 1 portaaviones de tamaño 5.
- 1 acorazado de tamaño 4
- 1 destructor de tamaño 3
- 1 lancha de tamaño 2

MEDIA
------
- Tablero 10x10.
- 50 disparos.
- 1 portaaviones de tamaño 5.
- 1 acorazado de tamaño 4
- 1 destructor de tamaño 3
- 1 submarino de tamaño 3
- 1 lancha de tamaño 2

DIFÍCIL
--------
- Tablero 10x10.
- 40 disparos.
- 1 portaaviones de tamaño 5.
- 1 acorazado de tamaño 4
- 1 destructor de tamaño 3
- 1 submarino de tamaño 3
- 1 lancha de tamaño 2

------------------------------------------------------------
Pulsa ENTER para volver al menú...
============================================================
"""