DIFICULTAD = {
    # PVE
    "PVE": {
        # Fácil
        1: {
            "nombre": "Fácil",
            "ancho": 4,
            "alto": 4,
            "disparos": 60,
            "barcos": [
                # ("Portaaviones", 5, "P"),
                # ("Acorazado", 4, "A"),
                # ("Submarino", 3, "S"),
                ("Lancha", 2, "L"),
            ]
        },

        # Media
        2: {
            "nombre": "Media",
            "ancho": 10,
            "alto": 10,
            "disparos": 50,
            "barcos": [
                ("Portaaviones", 5, "P"),
                ("Acorazado", 4, "A"),
                ("Destructor", 3, "D"),
                ("Submarino", 3, "S"),
                ("Lancha", 2, "L"),
            ]
        },

        # Difícil
        3: {
            "nombre": "Difícil",
            "ancho": 10,
            "alto": 10,
            "disparos": 40,
            "barcos": [
                ("Portaaviones", 5, "P"),
                ("Acorazado", 4, "A"),
                ("Destructor", 3, "D"),
                ("Submarino", 3, "S"),
                ("Lancha", 2, "L"),
            ]
        },
    },
    
    # PVP
    "PVP": {
        "ancho": 10,
        "alto": 10,
        "barcos": [
            ("Portaaviones", 5, "P"),
            ("Acorazado", 4, "A"),
            ("Destructor", 3, "D"),
            ("Submarino", 3, "S"),
            ("Lancha", 2, "L"),
        ]
    }
}

# Caracteres comunes
CARACTER_VACIO = "~"
CARACTER_TOCADO = "X"
CARACTER_AGUA = "O"
