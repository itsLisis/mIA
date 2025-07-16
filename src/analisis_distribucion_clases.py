import pandas as pd

# Cargar el dataset limpio
ruta = '../data/dataset_completo_clean.csv'
df = pd.read_csv(ruta)

print('Distribución de Perfil Personalidad:')
print(df['Perfil Personalidad'].value_counts())
print('\nDistribución de Sector Preferido:')
print(df['Sector Preferido'].value_counts()) 