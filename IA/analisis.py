def detectar_cambios_bruscos(df, columna, umbral=5):
    """Identifica si una variable cambia más de 'umbral' veces."""
    cambios = (df[columna] != df[columna].shift(1)).sum()
    return cambios > umbral

def filtrar_por_valor(df, columna, valor):
    """Filtra filas donde una columna tiene un valor específico (ej: corriente=0)."""
    return df[df[columna] == valor].index.tolist()