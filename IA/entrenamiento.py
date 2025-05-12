import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# Rutas
ruta_modelo = "modelos/modelo_fallos.pkl"
archivo_base = "datos_locomotoras.csv"
archivo_nuevos = "nuevos_registros.csv"

# Función para cargar y unir datos
def cargar_y_actualizar_datos():
    # Cargar datos existentes
    if os.path.exists(archivo_base):
        df_base = pd.read_csv(archivo_base)
    else:
        df_base = pd.DataFrame()

    # Cargar nuevos datos
    if os.path.exists(archivo_nuevos):
        df_nuevos = pd.read_csv(archivo_nuevos)

        # Evitar duplicados
        if not df_base.empty:
            df_total = pd.concat([df_base, df_nuevos]).drop_duplicates()
        else:
            df_total = df_nuevos

        # Guardar dataset actualizado
        df_total.to_csv(archivo_base, index=False)
        print("Datos nuevos incorporados a 'datos_locomotoras.csv'")
    else:
        df_total = df_base

    if df_total.empty:
        raise Exception("⚠️ No hay datos disponibles para entrenar.")
    
    return df_total

# Cargar y actualizar
df = cargar_y_actualizar_datos()

# Verificar columna de salida
if "fails" not in df.columns:
    raise Exception("Falta la columna 'fails' en el dataset.")

# Separar características y etiquetas
X = df.drop(columns=["fails"])
y = df["fails"]

# Dividir dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluar
y_pred = model.predict(X_test)
print("Evaluación del modelo:")
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Guardar modelo actualizado
os.makedirs("modelos", exist_ok=True)
joblib.dump(model, ruta_modelo)
print("Modelo actualizado guardado en:", ruta_modelo)

# Limpiar archivo de nuevos datos (opcional)
if os.path.exists(archivo_nuevos):
    os.remove(archivo_nuevos)
    print("'nuevos_registros.csv' limpiado tras entrenamiento.")
