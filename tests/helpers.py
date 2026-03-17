def contar_celdas_barco(tablero):
    """Cuenta cuántas celdas del tablero contienen partes de barcos."""
    contador = 0
    for fila in tablero:
        for celda in fila:
            if celda not in ["~", "X", "O"]:
                contador += 1
    return contador
    
    
def total_caracteres_barcos(lista_barcos):
    """Calcula el número total de celdas que deberían ocupar todos los barcos."""
    return sum(barco.tamanyo for barco in lista_barcos)