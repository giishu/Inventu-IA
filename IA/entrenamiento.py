import pandas as pd
from sklearn.model_selection import train_test_split

# Cargar CSV
df = pd.read_csv("datos_locomotoras.csv")

# Dividir datos (ej: "fallo" es la columna objetivo)
x = df.drop(columns=["fails"])  # Elimina la columna "fails" para crear X
y = df["fails"]                
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2)