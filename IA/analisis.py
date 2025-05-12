def detectar_cambios_bruscos(df, columna, umbral=1000):
    """
    Devuelve las filas donde la diferencia con la fila anterior supera el umbral.
    """
    df_filtrado = df.copy()
    
    # Nos aseguramos de que esté ordenado temporalmente
    df_filtrado = df_filtrado.sort_values(by="timestring")
    
    # Calculamos la diferencia absoluta entre cada fila y la anterior
    df_filtrado["diferencia"] = df_filtrado[columna].diff().abs()

    # Seleccionamos las filas donde la diferencia supera el umbral
    cambios = df_filtrado[df_filtrado["diferencia"] > umbral]

    return cambios[["timestring", "varname", columna, "diferencia"]]


def filtrar_por_valor(df, columna, valor):
    """Filtra filas donde una columna tiene un valor específico (ej: corriente=0)."""
    return df[df[columna] == valor]