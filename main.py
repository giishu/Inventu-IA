from IA.datos import cargar_csv

df = cargar_csv("data/LOG ENTRADAS Y SALIDAS FISICAS0.csv")
print(df.head(11))
print(df.dtypes)
