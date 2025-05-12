import pandas as pd
import joblib

# Cargar el modelo previamente entrenado
model = joblib.load("modelos/modelo_fallos.pkl")

# Cargar el archivo CSV de los nuevos datos
df_new = pd.read_csv("datos_nuevos.csv")

# Asegurarse de que los valores de los sensores sean numéricos
df_new["VarValue"] = df_new["VarValue"].astype(str).str.replace(",", ".").astype(float)

# Eliminar la columna TimeString porque no se usa en la predicción
df_new = df_new.drop(columns=["TimeString"])

# De ser necesario, convertir a un formato de tabla similar a lo entrenado (con columnas como 'RPM', 'IMT1', 'IMT3', etc.)
df_new = df_new.pivot_table(
    index="TimeString",
    columns="VarName",
    values="VarValue",
    aggfunc="mean"
).reset_index()

# Predecir con el modelo cargado
predicciones = model.predict(df_new)

# Mostrar las predicciones
for index, prediction in enumerate(predicciones):
    print(f"Fila {index}: {'Fallo' if prediction == 1 else 'Sin fallo'}")

# Guardar las predicciones junto con los datos
df_new["Prediccion_Fallo"] = predicciones
df_new.to_csv("predicciones_fallos.csv", index=False)
