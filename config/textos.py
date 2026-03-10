from modelo.resultado import ResultadoDisparo

TRADUCCION = {
    ResultadoDisparo.AGUA: "AGUA",
    ResultadoDisparo.TOCADO: "TOCADO",
    ResultadoDisparo.HUNDIDO: "TOCADO_Y_HUNDIDO",
    ResultadoDisparo.REPETIDO: "REPETIDO",
    ResultadoDisparo.INVALIDO: "INVALIDO",
}

TEXTOS = {
    "TURNO": "TURNO DEL JUGADOR {}",
    
    # Inputs
    "POSICION_X": "Introduzca la coordenada x: ",
    "POSICION_Y": "Introduzca la coordenada y: ",
    "PULSAR_ENTER" : "\nPulsa Enter para continuar...",

    # Disparos
    "TOCADO_Y_HUNDIDO": "TOCADO Y HUNDIDO",
    "TOCADO": "TOCADO",
    "AGUA": "AGUA",
    "REPETIDO": "YA HABÍAS DISPARADO EN ESTE HUECO. NO PIERDES LA BALA.",
    "BALAS_RESTANTES": "BALAS RESTANTES: ",

    # Final
    "VICTORIA": "¡VICTORIA! TE HAS CARGADO TODOS LOS BARCOS, ENHORABUENA.",
    "DERROTA": "¡DERROTA! AFINA TU PUNTERÍA Y VUELVE A INTENTARLO.",
    "ABANDONO_PVP" : "VICTORIA, TU RIVAL SE HA DESCONECTADO. PULSA INTRO PARA CONTINUAR...",
    
    # Terminar programa
    "FIN_JUEGO" : "Escriba 'Salir' para volver al menú.",
    "FIN_DE_PROGRAMA" : "FIN DE PROGRAMA",

    # Errores
    "ERROR_LIMITE_TABLERO": "ERROR: La posición del disparo excede los límites del tablero",
    "ERROR_NUMERO_ENTERO": "ERROR: Introduce números enteros, por favor",
    "ERROR_MENU" : "ERROR: Opción inválida",
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