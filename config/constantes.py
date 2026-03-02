DIFICULTAD = {
    
    # Fácil
    1: {
        "ancho": 8,
        "alto": 8,
        "disparos": 60,
        "barcos": [
            ("Portaaviones", 5, 1, "P"),
            ("Acorazado", 4, 1, "A"),
            ("Submarino", 3, 1, "S"),
            ("Lancha", 2, 1, "L"),
        ]
    },

    # Media
    2: {
        "ancho": 10,
        "alto": 10,
        "disparos": 50,
        "barcos": [
            ("Portaaviones", 5, 1, "P"),
            ("Acorazado", 4, 1, "A"),
            ("Destructor", 3, 1, "D"),
            ("Submarino", 3, 1, "S"),
            ("Lancha", 2, 1, "L"),
        ]
    },

    # Difícil
    3: {
        "ancho": 10,
        "alto": 10,
        "disparos": 40,
        "barcos": [
            ("Portaaviones", 5, 1, "P"),
            ("Acorazado", 4, 1, "A"),
            ("Destructor", 3, 1, "D"),
            ("Submarino", 3, 1, "S"),
            ("Lancha", 2, 1, "L"),
        ]
    },
    
    # PVP
    "PVP": {
        "ancho": 10,
        "alto": 10,
        "barcos": [
            ("Portaaviones", 5, 1, "P"),
            ("Acorazado", 4, 1, "A"),
            ("Destructor", 3, 1, "D"),
            ("Submarino", 3, 1, "S"),
            ("Lancha", 2, 1, "L"),
        ]
    }
}

# Caracteres comunes
CARACTER_VACIO = "~"
CARACTER_TOCADO = "X"
CARACTER_AGUA = "O"
