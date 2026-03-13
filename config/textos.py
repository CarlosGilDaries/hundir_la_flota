from modelo.resultado import ResultadoDisparo

TRADUCCION = {
    ResultadoDisparo.AGUA: "AGUA",
    ResultadoDisparo.TOCADO: "TOCADO",
    ResultadoDisparo.HUNDIDO: "HUNDIDO",
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
    "HUNDIDO": "TOCADO Y HUNDIDO",
    "TOCADO": "TOCADO",
    "AGUA": "AGUA",
    "REPETIDO": "YA HABÍAS DISPARADO EN ESTE HUECO. NO PIERDES LA BALA.",
    "REPETIDO_PVP": "DISPARO REPETIDO. SE PIERDE LA BALA.",
    "BALAS_RESTANTES": "BALAS RESTANTES: ",

    # Final
    "VICTORIA": "¡VICTORIA! TE HAS CARGADO TODOS LOS BARCOS, ENHORABUENA.",
    "DERROTA": "¡DERROTA! AFINA TU PUNTERÍA Y VUELVE A INTENTARLO.",
    "ABANDONO_PVP" : "\nVICTORIA, TU RIVAL SE HA DESCONECTADO. PULSA INTRO PARA CONTINUAR...",
    
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
            ------------------------
            PVE (Jugador vs Máquina)
            ------------------------
            El jugador se enfrentará a la máquina. La máquina colocará los barcos
            aleatoriamente en el tablero. El jugador dispondrá de una cantidad
            limitada de disparos para intentar derribar todos los barcos enemigos.

            Las dimensiones del tablero, la cantidad de disparos y la cantidad de
            barcos dependerán de la dificultad seleccionada.

            ------------------------
            PVP (Jugador vs Jugador)
            ------------------------
            El jugador se conectará a un servidor y será emparejado con otro jugador
            en cola, iniciando una partida 1 vs 1.

            Primero se realizará una fase de colocación de barcos. El programa
            mostrará una lista de barcos con su tamaño, por ejemplo:

            1. Portaaviones (5)

            Tras seleccionar un barco, el jugador deberá introducir:
            - Las coordenadas de la primera casilla del barco
            - La orientación (horizontal o vertical)

            Cuando ambos jugadores hayan colocado todos sus barcos, el sistema
            asignará el orden de turnos aleatoriamente y comenzará la fase de
            disparos contra el tablero rival.

            ============================================================

            DIFICULTADES (Modo PVE)

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
            
            MUY DIFÍCIL
            --------
            - Tablero 12x12.
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