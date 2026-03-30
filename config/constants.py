# config/constants.py

CONSTANTS = {
    "DIFFICULTY": {
        # PVE
        "PVE": {
            # Easy
            1: {
                "name": "Fácil",
                "width": 8,
                "height": 8,
                "shots": 60,
                "ships": [
                    ("Portaaviones", 5, "P"),
                    ("Acorazado", 4, "A"),
                    ("Submarino", 3, "S"),
                    ("Lancha", 2, "L"),
                ]
            },

            # Medium
            2: {
                "name": "Media",
                "width": 10,
                "height": 10,
                "shots": 50,
                "ships": [
                    ("Portaaviones", 5, "P"),
                    ("Acorazado", 4, "A"),
                    ("Destructor", 3, "D"),
                    ("Submarino", 3, "S"),
                    ("Lancha", 2, "L"),
                ]
            },

            # Hard
            3: {
                "name": "Difícil",
                "width": 10,
                "height": 10,
                "shots": 40,
                "ships": [
                    ("Portaaviones", 5, "P"),
                    ("Acorazado", 4, "A"),
                    ("Destructor", 3, "D"),
                    ("Submarino", 3, "S"),
                    ("Lancha", 2, "L"),
                ]
            },

            # Very Hard
            4: {
                "name": "Muy Difícil",
                "width": 12,
                "height": 12,
                "shots": 40,
                "ships": [
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
            "width": 10,
            "height": 10,
            "ships": [
                ("Portaaviones", 5, "P"),
                ("Acorazado", 4, "A"),
                ("Destructor", 3, "D"),
                ("Submarino", 3, "S"),
                ("Lancha", 2, "L"),
            ]
        }
    },

    # Common characters
    "CHARACTERS": {
        "EMPTY_CHARACTER": "~",
        "HIT_CHARACTER": "X",
        "WATER_CHARACTER": "O"
    }
}