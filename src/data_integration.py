import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class DataIntegrator:
    """
    Clase para integrar y preprocesar datos de formularios y notas académicas
    """
    
    def __init__(self, formulario_path: str, notas_path: str):
        """
        Inicializa el integrador de datos
        
        Args:
            formulario_path: Ruta al archivo CSV de respuestas del formulario
            notas_path: Ruta al archivo CSV de notas académicas
        """
        self.formulario_path = formulario_path
        self.notas_path = notas_path
        self.df_combined = None
        self.materias = [
            "Física", "Biología y química", "Educación artística", "Ciencias sociales",
            "Educación física", "Matemáticas", "Lengua castellana", "Ciencias económicas y políticas"
        ]
    
    def load_data(self) -> pd.DataFrame:
        """
        Carga y combina los dos archivos CSV
        
        Returns:
            DataFrame combinado
        """
        print("Cargando datos...")
        
        # Cargar formulario
        df_formulario = pd.read_csv(self.formulario_path, encoding='utf-8')
        print(f"Formulario cargado: {len(df_formulario)} estudiantes")
        
        # Cargar notas
        df_notas = pd.read_csv(self.notas_path, encoding='utf-8')
        print(f"Notas cargadas: {len(df_notas)} estudiantes")
        
        # Combinar por nombre del estudiante
        self.df_combined = pd.merge(df_formulario, df_notas, on='Nombre completo', how='inner')
        print(f"Dataset combinado: {len(self.df_combined)} estudiantes")
        
        # Limpiar datos
        self._clean_data()
        
        return self.df_combined
    
    def _clean_data(self) -> None:
        """
        Limpia los datos eliminando valores problemáticos
        """
        print("Limpiando datos...")
        
        # Reemplazar valores nulos en columnas de texto con string vacío
        text_columns = [
            '¿Cuáles son las materias que te gustan MÁS?',
            '¿Cuáles son las materias que te gustan MENOS?',
            '¿En qué materias te va MEJOR?',
            '¿En qué materias NO TE VA BIEN?',
            '¿Cómo te ves a ti mismo? Como alguien...',
            '¿En cuál de estos sectores te gustaría trabajar?'
        ]
        
        for col in text_columns:
            if col in self.df_combined.columns:
                self.df_combined[col] = self.df_combined[col].fillna('')
        
        print("Datos limpiados exitosamente")
    
    def calculate_averages(self) -> pd.DataFrame:
        """
        Calcula promedios por materia y promedio general
        
        Returns:
            DataFrame con promedios añadidos
        """
        print("Calculando promedios...")
        
        # Calcular promedio por materia
        for materia in self.materias:
            trimestre_cols = [f"{materia} - Trimestre {i}" for i in range(1, 5)]
            
            # Verificar que las columnas existen
            existing_cols = [col for col in trimestre_cols if col in self.df_combined.columns]
            
            if existing_cols:
                self.df_combined[f"{materia} - Promedio"] = self.df_combined[existing_cols].mean(axis=1)
        
        # Calcular promedio general (todas las materias)
        promedio_cols = [f"{materia} - Promedio" for materia in self.materias 
                        if f"{materia} - Promedio" in self.df_combined.columns]
        
        if promedio_cols:
            self.df_combined['Promedio General'] = self.df_combined[promedio_cols].mean(axis=1)
        
        print("Promedios calculados exitosamente")
        return self.df_combined
    
    def classify_performance(self) -> pd.DataFrame:
        """
        Clasifica el rendimiento en Alto, Medio, Bajo basado en el promedio general
        
        Returns:
            DataFrame con clasificación añadida
        """
        print("Clasificando rendimiento...")
        
        def classify_student(promedio):
            if promedio >= 4.0:
                return "Alto"
            elif promedio >= 3.0:
                return "Medio"
            else:
                return "Bajo"
        
        # Clasificar rendimiento general
        self.df_combined['Rendimiento General'] = self.df_combined['Promedio General'].apply(classify_student)
        
        # Clasificar rendimiento por materia
        for materia in self.materias:
            promedio_col = f"{materia} - Promedio"
            if promedio_col in self.df_combined.columns:
                self.df_combined[f"{materia} - Rendimiento"] = self.df_combined[promedio_col].apply(classify_student)
        
        print("Clasificación de rendimiento completada")
        return self.df_combined
    
    def analyze_form_responses(self) -> pd.DataFrame:
        """
        Analiza las respuestas del formulario y crea variables derivadas
        
        Returns:
            DataFrame con análisis añadido
        """
        print("Analizando respuestas del formulario...")
        
        # Contar materias favoritas
        self.df_combined['Cantidad Materias Favoritas'] = self.df_combined['¿Cuáles son las materias que te gustan MÁS?'].apply(
            self._count_materias
        )
        
        # Contar materias que no gustan
        self.df_combined['Cantidad Materias No Favoritas'] = self.df_combined['¿Cuáles son las materias que te gustan MENOS?'].apply(
            self._count_materias
        )
        
        # Contar materias en las que va bien
        self.df_combined['Cantidad Materias Buenas'] = self.df_combined['¿En qué materias te va MEJOR?'].apply(
            self._count_materias
        )
        
        # Contar materias en las que va mal
        self.df_combined['Cantidad Materias Malas'] = self.df_combined['¿En qué materias NO TE VA BIEN?'].apply(
            self._count_materias
        )
        
        # Crear indicador de coherencia (materias favoritas que también van bien)
        self.df_combined['Coherencia Gustos-Rendimiento'] = self.df_combined.apply(
            self._calculate_coherence, axis=1
        )
        
        # Clasificar perfil de personalidad
        self.df_combined['Perfil Personalidad'] = self.df_combined['¿Cómo te ves a ti mismo? Como alguien...'].apply(
            self._classify_personality
        )
        
        # Clasificar sector laboral preferido
        self.df_combined['Sector Preferido'] = self.df_combined['¿En cuál de estos sectores te gustaría trabajar?'].apply(
            self._classify_sector
        )
        
        print("Análisis de formulario completado")
        return self.df_combined
    
    def _count_materias(self, x) -> int:
        """
        Cuenta el número de materias en una cadena separada por comas
        """
        try:
            if pd.isna(x) or str(x).strip() == '' or str(x).strip() == 'nan':
                return 0
            
            materias = [m.strip() for m in str(x).split(',') if m.strip()]
            return len(materias)
        except Exception:
            return 0
    
    def _calculate_coherence(self, row) -> str:
        """
        Calcula la coherencia entre gustos y rendimiento
        """
        # Manejar valores nulos
        materias_favoritas_str = str(row['¿Cuáles son las materias que te gustan MÁS?']).strip()
        materias_buenas_str = str(row['¿En qué materias te va MEJOR?']).strip()
        
        if materias_favoritas_str == 'nan' or materias_favoritas_str == '':
            return "Sin datos"
        
        materias_favoritas = [m.strip() for m in materias_favoritas_str.split(',') if m.strip()]
        materias_buenas = [m.strip() for m in materias_buenas_str.split(',') if m.strip()]
        
        coherentes = set(materias_favoritas) & set(materias_buenas)
        total_favoritas = len(materias_favoritas)
        
        if total_favoritas == 0:
            return "Sin datos"
        
        porcentaje = len(coherentes) / total_favoritas
        
        if porcentaje >= 0.7:
            return "Muy Coherente"
        elif porcentaje >= 0.4:
            return "Coherente"
        else:
            return "Poco Coherente"
    
    def _classify_personality(self, personalidad: str) -> str:
        """
        Clasifica el perfil de personalidad con mejor balanceo
        """
        personalidad_str = str(personalidad).lower()
        
        if 'curioso' in personalidad_str:
            return "Investigador"
        elif 'imaginativo' in personalidad_str:
            return "Artístico"
        elif 'hábil' in personalidad_str:
            return "Técnico"
        elif 'líder' in personalidad_str:
            return "Líder"
        elif 'organizado' in personalidad_str:
            return "Organizador"
        elif 'sociable' in personalidad_str:
            return "Social"
        else:
            return "Mixto"
    
    def _classify_sector(self, sectores: str) -> str:
        """
        Clasifica el sector laboral preferido con mejor balanceo
        """
        sectores_str = str(sectores).lower()
        
        if 'educación' in sectores_str or 'desarrollo humano' in sectores_str:
            return "Educativo"
        elif 'salud' in sectores_str:
            return "Salud"
        elif 'tic' in sectores_str or 'tecnologías' in sectores_str or 'telecomunicaciones' in sectores_str:
            return "Tecnología"
        elif 'cultural' in sectores_str or 'artístico' in sectores_str:
            return "Cultural"
        elif 'industrial' in sectores_str or 'construcción' in sectores_str or 'manufacturero' in sectores_str:
            return "Industrial"
        elif 'investigación' in sectores_str or 'ciencias básicas' in sectores_str:
            return "Investigación"
        else:
            return "Otros"
    
    def generate_summary_stats(self) -> Dict:
        """
        Genera estadísticas resumidas del dataset
        
        Returns:
            Diccionario con estadísticas
        """
        print("Generando estadísticas resumidas...")
        
        stats = {
            'total_estudiantes': len(self.df_combined),
            'rendimiento_alto': len(self.df_combined[self.df_combined['Rendimiento General'] == 'Alto']),
            'rendimiento_medio': len(self.df_combined[self.df_combined['Rendimiento General'] == 'Medio']),
            'rendimiento_bajo': len(self.df_combined[self.df_combined['Rendimiento General'] == 'Bajo']),
            'promedio_general_dataset': self.df_combined['Promedio General'].mean(),
            'materia_mejor_promedio': self._get_best_subject(),
            'materia_peor_promedio': self._get_worst_subject(),
            'perfiles_personales': self.df_combined['Perfil Personalidad'].value_counts().to_dict(),
            'sectores_preferidos': self.df_combined['Sector Preferido'].value_counts().to_dict()
        }
        
        return stats
    
    def _get_best_subject(self) -> str:
        """Obtiene la materia con mejor promedio"""
        promedio_cols = [f"{materia} - Promedio" for materia in self.materias 
                        if f"{materia} - Promedio" in self.df_combined.columns]
        
        if promedio_cols:
            promedios = self.df_combined[promedio_cols].mean()
            return promedios.idxmax().replace(' - Promedio', '')
        return "N/A"
    
    def _get_worst_subject(self) -> str:
        """Obtiene la materia con peor promedio"""
        promedio_cols = [f"{materia} - Promedio" for materia in self.materias 
                        if f"{materia} - Promedio" in self.df_combined.columns]
        
        if promedio_cols:
            promedios = self.df_combined[promedio_cols].mean()
            return promedios.idxmin().replace(' - Promedio', '')
        return "N/A"
    
    def save_clean_data(self, output_path: str) -> None:
        """
        Guarda el dataset limpio y fusionado
        
        Args:
            output_path: Ruta donde guardar el archivo CSV
        """
        print(f"Guardando dataset limpio en: {output_path}")
        self.df_combined.to_csv(output_path, index=False, encoding='utf-8')
        print("Dataset guardado exitosamente")
    
    def run_full_integration(self, output_path: str, balance_data: bool = True, target_samples_per_class: int = 1000) -> pd.DataFrame:
        """
        Ejecuta todo el proceso de integración y preprocesamiento
        
        Args:
            output_path: Ruta donde guardar el archivo CSV final
            balance_data: Si se debe balancear el dataset
            target_samples_per_class: Número objetivo de muestras por clase
            
        Returns:
            DataFrame procesado
        """
        print("=== INICIANDO PROCESO DE INTEGRACIÓN Y PREPROCESAMIENTO ===")
        
        # 1. Cargar y combinar datos
        self.load_data()
        
        # 2. Calcular promedios
        self.calculate_averages()
        
        # 3. Clasificar rendimiento
        self.classify_performance()
        
        # 4. Analizar respuestas del formulario
        self.analyze_form_responses()
        
        # 5. Balancear dataset si se solicita
        if balance_data:
            self.balance_dataset(target_samples_per_class)
        
        # 6. Generar estadísticas
        stats = self.generate_summary_stats()
        
        # 7. Guardar datos limpios
        self.save_clean_data(output_path)
        
        # 8. Mostrar resumen
        self._print_summary(stats)
        
        print("=== PROCESO COMPLETADO ===")
        
        return self.df_combined
    
    def balance_dataset(self, target_samples_per_class: int = None) -> pd.DataFrame:
        """
        Balancea el dataset para que todas las clases tengan una distribución similar
        
        Args:
            target_samples_per_class: Número objetivo de muestras por clase. Si es None, usa el mínimo
            
        Returns:
            DataFrame balanceado
        """
        print("Balanceando dataset...")
        
        # Balancear perfiles de personalidad
        self._balance_class('Perfil Personalidad', target_samples_per_class)
        
        # Balancear sectores preferidos
        self._balance_class('Sector Preferido', target_samples_per_class)
        
        print(f"Dataset balanceado: {len(self.df_combined)} estudiantes")
        return self.df_combined
    
    def _balance_class(self, column_name: str, target_samples: int = None) -> None:
        """
        Balancea una columna específica del dataset
        
        Args:
            column_name: Nombre de la columna a balancear
            target_samples: Número objetivo de muestras por clase
        """
        if column_name not in self.df_combined.columns:
            return
        
        # Obtener conteo de cada clase
        class_counts = self.df_combined[column_name].value_counts()
        print(f"\nDistribución original de {column_name}:")
        for clase, count in class_counts.items():
            print(f"  {clase}: {count}")
        
        # Determinar el número objetivo de muestras por clase
        if target_samples is None:
            # Asegurar al menos 50 muestras por clase para cross-validation
            min_samples = max(class_counts.min(), 50)
            target_samples = min_samples
        
        print(f"Objetivo: {target_samples} muestras por clase")
        
        # Crear dataset balanceado
        balanced_dfs = []
        
        for clase in class_counts.index:
            class_data = self.df_combined[self.df_combined[column_name] == clase]
            
            if len(class_data) > target_samples:
                # Si hay más muestras de las necesarias, hacer muestreo aleatorio
                balanced_class = class_data.sample(n=target_samples, random_state=42)
            else:
                # Si hay menos muestras, hacer oversampling con reemplazo
                balanced_class = class_data.sample(n=target_samples, replace=True, random_state=42)
            
            balanced_dfs.append(balanced_class)
        
        # Combinar todos los datasets balanceados
        self.df_combined = pd.concat(balanced_dfs, ignore_index=True)
        
        # Mezclar el dataset final
        self.df_combined = self.df_combined.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Mostrar nueva distribución
        new_class_counts = self.df_combined[column_name].value_counts()
        print(f"\nDistribución balanceada de {column_name}:")
        for clase, count in new_class_counts.items():
            print(f"  {clase}: {count}")
    
    def _print_summary(self, stats: Dict) -> None:
        """
        Imprime un resumen de los resultados
        """
        print("\n" + "="*50)
        print("RESUMEN DEL PROCESAMIENTO")
        print("="*50)
        print(f"Total de estudiantes procesados: {stats['total_estudiantes']}")
        print(f"Promedio general del dataset: {stats['promedio_general_dataset']:.2f}")
        print(f"Rendimiento Alto: {stats['rendimiento_alto']} estudiantes")
        print(f"Rendimiento Medio: {stats['rendimiento_medio']} estudiantes")
        print(f"Rendimiento Bajo: {stats['rendimiento_bajo']} estudiantes")
        print(f"Materia con mejor promedio: {stats['materia_mejor_promedio']}")
        print(f"Materia con peor promedio: {stats['materia_peor_promedio']}")
        print("\nPerfiles de personalidad más comunes:")
        for perfil, cantidad in list(stats['perfiles_personales'].items())[:3]:
            print(f"  - {perfil}: {cantidad} estudiantes")
        print("\nSectores laborales más preferidos:")
        for sector, cantidad in list(stats['sectores_preferidos'].items())[:3]:
            print(f"  - {sector}: {cantidad} estudiantes")
        print("="*50)


def main():
    """
    Función principal para ejecutar la integración de datos
    """
    # Configurar rutas
    formulario_path = "../data/respuestas_formulario.csv"
    notas_path = "../data/notas_academicas.csv"
    output_path = "../data/dataset_completo.csv"
    
    # Crear instancia del integrador
    integrator = DataIntegrator(formulario_path, notas_path)
    
    # Ejecutar integración completa con balanceo
    df_final = integrator.run_full_integration(output_path, balance_data=True, target_samples_per_class=1200)
    
    print(f"\nDataset final tiene {len(df_final)} filas y {len(df_final.columns)} columnas")
    print(f"Archivo guardado en: {output_path}")


if __name__ == "__main__":
    main() 