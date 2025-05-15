import pandas as pd

def detectar_cambios_bruscos(df, columna, umbral=1000):
    """
    Versión mejorada que maneja mejor los nombres de columnas
    """
    try:
        # Verificar que la columna existe
        if columna not in df.columns:
            raise KeyError(f"Columna '{columna}' no encontrada")
            
        # Verificar que es numérica
        if not pd.api.types.is_numeric_dtype(df[columna]):
            raise ValueError(f"Columna '{columna}' no es numérica")
        
        # Ordenar por tiempo si existe la columna
        time_col = next((c for c in df.columns if 'time' in c.lower()), None)
        if time_col:
            df = df.sort_values(time_col)
        
        # Calcular diferencias
        df['Diferencia_temp'] = df[columna].diff().abs()
        
        # Filtrar cambios bruscos
        cambios = df[df['Diferencia_temp'] > umbral].copy()
        
        if not cambios.empty:
            cambios['Tipo_Falla'] = f'Cambio brusco (> {umbral})'
            cambios['Valor_anterior'] = df[columna].shift(1).loc[cambios.index]
            cambios['Diferencia'] = cambios['Diferencia_temp']
        
        return cambios.drop(columns=['Diferencia_temp'], errors='ignore')
        
    except Exception as e:
        print(f"Error en detectar_cambios_bruscos: {str(e)}")
        return pd.DataFrame()

def analizar_tendencia(df, columna, ventana=30):
    """Analiza desgaste progresivo (media móvil)"""
    if columna not in df.columns:
        raise ValueError(f"Columna {columna} no existe")
    
    df['tendencia'] = (
        df[columna]
        .astype(float)
        .rolling(ventana)
        .mean()
    )
    return df[['"timestring"', columna, 'tendencia']].dropna()