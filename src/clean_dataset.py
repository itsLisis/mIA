import pandas as pd
import numpy as np

def clean_dataset():
    """
    Limpia el dataset existente y corrige los valores NaN
    """
    print("Limpiando dataset existente...")
    
    # Cargar el dataset
    df = pd.read_csv('../data/dataset_completo.csv', encoding='utf-8')
    print(f"Dataset cargado: {len(df)} filas, {len(df.columns)} columnas")
    
    # Verificar columnas con valores NaN
    nan_columns = df.columns[df.isnull().any()].tolist()
    print(f"Columnas con valores NaN: {nan_columns}")
    
    # Limpiar columnas de cantidad de materias
    materias_columns = [
        'Cantidad Materias Favoritas',
        'Cantidad Materias No Favoritas', 
        'Cantidad Materias Buenas',
        'Cantidad Materias Malas'
    ]
    
    for col in materias_columns:
        if col in df.columns:
            # Reemplazar NaN con 0
            df[col] = df[col].fillna(0)
            print(f"Limpieza de {col}: {df[col].isnull().sum()} valores NaN reemplazados")
    
    # Limpiar otras columnas numéricas
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if df[col].isnull().any():
            # Reemplazar con la mediana
            median_val = df[col].median()
            if pd.isna(median_val):
                median_val = 0.0
            df[col] = df[col].fillna(median_val)
            print(f"Limpieza de {col}: valores NaN reemplazados con mediana {median_val:.2f}")
    
    # Limpiar columnas de texto
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna('')
            print(f"Limpieza de {col}: valores NaN reemplazados con string vacío")
    
    # Verificar que no queden valores NaN
    remaining_nan = df.isnull().sum().sum()
    print(f"Valores NaN restantes: {remaining_nan}")
    
    # Guardar dataset limpio
    df.to_csv('../data/dataset_completo_clean.csv', index=False, encoding='utf-8')
    print("Dataset limpio guardado en: ../data/dataset_completo_clean.csv")
    
    return df

if __name__ == "__main__":
    clean_dataset() 