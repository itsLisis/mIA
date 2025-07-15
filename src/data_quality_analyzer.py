import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataQualityAnalyzer:
    """
    Analizador de calidad de datos para el sistema vocacional
    """
    
    def __init__(self, data_path: str = "data/dataset_completo.csv"):
        self.data_path = data_path
        self.df = None
        self.analysis_results = {}
        
    def load_data(self) -> pd.DataFrame:
        """
        Cargar datos
        """
        print("Cargando datos para análisis...")
        self.df = pd.read_csv(self.data_path, encoding='utf-8')
        print(f"Datos cargados: {len(self.df)} filas, {len(self.df.columns)} columnas")
        return self.df
    
    def analyze_missing_data(self) -> Dict:
        """
        Analizar datos faltantes
        """
        print("\n=== ANÁLISIS DE DATOS FALTANTES ===")
        
        missing_data = self.df.isnull().sum()
        missing_percentage = (missing_data / len(self.df)) * 100
        
        missing_analysis = pd.DataFrame({
            'columna': missing_data.index,
            'valores_faltantes': missing_data.values,
            'porcentaje_faltante': missing_percentage.values
        }).sort_values('porcentaje_faltante', ascending=False)
        
        print("Columnas con datos faltantes:")
        for _, row in missing_analysis[missing_analysis['valores_faltantes'] > 0].iterrows():
            print(f"  - {row['columna']}: {row['valores_faltantes']} ({row['porcentaje_faltante']:.2f}%)")
        
        self.analysis_results['missing_data'] = missing_analysis
        return missing_analysis
    
    def analyze_target_distribution(self) -> Dict:
        """
        Analizar distribución de variables objetivo
        """
        print("\n=== ANÁLISIS DE DISTRIBUCIÓN DE VARIABLES OBJETIVO ===")
        
        targets = ['Perfil Personalidad', 'Sector Preferido']
        target_analysis = {}
        
        for target in targets:
            if target in self.df.columns:
                distribution = self.df[target].value_counts()
                print(f"\nDistribución de '{target}':")
                for category, count in distribution.items():
                    percentage = (count / len(self.df)) * 100
                    print(f"  - {category}: {count} ({percentage:.2f}%)")
                
                # Calcular balance
                total = len(self.df)
                max_count = distribution.max()
                min_count = distribution.min()
                balance_ratio = min_count / max_count
                
                print(f"  Balance ratio: {balance_ratio:.3f}")
                if balance_ratio < 0.3:
                    print("  ⚠️  DATOS DESBALANCEADOS - Considerar técnicas de balanceo")
                elif balance_ratio < 0.5:
                    print("  ⚠️  DATOS MODERADAMENTE DESBALANCEADOS")
                else:
                    print("  ✅ Datos relativamente balanceados")
                
                target_analysis[target] = {
                    'distribution': distribution,
                    'balance_ratio': balance_ratio,
                    'total_categories': len(distribution)
                }
        
        self.analysis_results['target_distribution'] = target_analysis
        return target_analysis
    
    def analyze_feature_correlations(self) -> pd.DataFrame:
        """
        Analizar correlaciones entre características
        """
        print("\n=== ANÁLISIS DE CORRELACIONES ===")
        
        # Seleccionar características numéricas
        numeric_features = self.df.select_dtypes(include=[np.number]).columns
        numeric_df = self.df[numeric_features]
        
        # Calcular correlaciones
        correlation_matrix = numeric_df.corr()
        
        # Encontrar correlaciones altas
        high_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.8:
                    high_correlations.append({
                        'feature1': correlation_matrix.columns[i],
                        'feature2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        print("Correlaciones altas (>0.8):")
        for corr in high_correlations:
            print(f"  - {corr['feature1']} ↔ {corr['feature2']}: {corr['correlation']:.3f}")
        
        self.analysis_results['correlations'] = {
            'matrix': correlation_matrix,
            'high_correlations': high_correlations
        }
        
        return correlation_matrix
    
    def analyze_feature_importance_estimate(self) -> pd.DataFrame:
        """
        Estimar importancia de características usando correlación con targets
        """
        print("\n=== ESTIMACIÓN DE IMPORTANCIA DE CARACTERÍSTICAS ===")
        
        # Codificar variables objetivo
        le_personalidad = LabelEncoder()
        le_sector = LabelEncoder()
        
        y_personalidad = le_personalidad.fit_transform(self.df['Perfil Personalidad'].fillna('Desconocido'))
        y_sector = le_sector.fit_transform(self.df['Sector Preferido'].fillna('Desconocido'))
        
        # Seleccionar características numéricas
        numeric_features = self.df.select_dtypes(include=[np.number]).columns
        feature_importance = []
        
        for feature in numeric_features:
            # Correlación con Perfil Personalidad
            corr_personalidad = np.corrcoef(self.df[feature], y_personalidad)[0, 1]
            if np.isnan(corr_personalidad):
                corr_personalidad = 0
            
            # Correlación con Sector Preferido
            corr_sector = np.corrcoef(self.df[feature], y_sector)[0, 1]
            if np.isnan(corr_sector):
                corr_sector = 0
            
            # Importancia promedio
            avg_importance = (abs(corr_personalidad) + abs(corr_sector)) / 2
            
            feature_importance.append({
                'feature': feature,
                'corr_personalidad': abs(corr_personalidad),
                'corr_sector': abs(corr_sector),
                'avg_importance': avg_importance
            })
        
        # Ordenar por importancia
        importance_df = pd.DataFrame(feature_importance).sort_values('avg_importance', ascending=False)
        
        print("Top 10 características más importantes:")
        for i, row in importance_df.head(10).iterrows():
            print(f"  {i+1}. {row['feature']}: {row['avg_importance']:.4f}")
        
        self.analysis_results['feature_importance'] = importance_df
        return importance_df
    
    def analyze_data_quality_issues(self) -> List[str]:
        """
        Identificar problemas de calidad de datos
        """
        print("\n=== PROBLEMAS DE CALIDAD DE DATOS IDENTIFICADOS ===")
        
        issues = []
        
        # 1. Verificar datos faltantes
        missing_cols = self.df.columns[self.df.isnull().sum() > 0]
        if len(missing_cols) > 0:
            issues.append(f"Hay {len(missing_cols)} columnas con datos faltantes")
        
        # 2. Verificar valores únicos en columnas categóricas
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_count = self.df[col].nunique()
            if unique_count == 1:
                issues.append(f"Columna '{col}' tiene solo un valor único - no útil para ML")
            elif unique_count == len(self.df):
                issues.append(f"Columna '{col}' tiene valores únicos para cada fila - posible ID")
        
        # 3. Verificar outliers en columnas numéricas
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = self.df[(self.df[col] < Q1 - 1.5*IQR) | (self.df[col] > Q3 + 1.5*IQR)]
            if len(outliers) > 0:
                issues.append(f"Columna '{col}' tiene {len(outliers)} outliers")
        
        # 4. Verificar balance de clases
        for target in ['Perfil Personalidad', 'Sector Preferido']:
            if target in self.df.columns:
                distribution = self.df[target].value_counts()
                balance_ratio = distribution.min() / distribution.max()
                if balance_ratio < 0.3:
                    issues.append(f"Variable '{target}' está muy desbalanceada (ratio: {balance_ratio:.3f})")
        
        # Imprimir problemas
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("  ✅ No se identificaron problemas graves de calidad de datos")
        
        self.analysis_results['quality_issues'] = issues
        return issues
    
    def generate_improvement_recommendations(self) -> Dict:
        """
        Generar recomendaciones para mejorar la precisión del modelo
        """
        print("\n=== RECOMENDACIONES PARA MEJORAR LA PRECISIÓN ===")
        
        recommendations = {
            'data_quality': [],
            'feature_engineering': [],
            'model_improvements': [],
            'data_collection': []
        }
        
        # Basado en análisis de datos faltantes
        if 'missing_data' in self.analysis_results:
            missing_cols = self.analysis_results['missing_data']
            high_missing = missing_cols[missing_cols['porcentaje_faltante'] > 20]
            if len(high_missing) > 0:
                recommendations['data_quality'].append(
                    f"Considerar eliminar o imputar {len(high_missing)} columnas con >20% datos faltantes"
                )
        
        # Basado en balance de clases
        if 'target_distribution' in self.analysis_results:
            for target, analysis in self.analysis_results['target_distribution'].items():
                if analysis['balance_ratio'] < 0.3:
                    recommendations['model_improvements'].append(
                        f"Usar técnicas de balanceo para '{target}' (SMOTE, undersampling, etc.)"
                    )
        
        # Basado en correlaciones
        if 'correlations' in self.analysis_results:
            high_corr = self.analysis_results['correlations']['high_correlations']
            if len(high_corr) > 0:
                recommendations['feature_engineering'].append(
                    f"Considerar eliminar una de las {len(high_corr)} pares de características altamente correlacionadas"
                )
        
        # Recomendaciones generales
        recommendations['feature_engineering'].extend([
            "Crear características derivadas (ratios, diferencias, promedios)",
            "Aplicar técnicas de normalización/estandarización",
            "Usar selección de características (SelectKBest, RFE)"
        ])
        
        recommendations['model_improvements'].extend([
            "Probar modelos ensemble (RandomForest, GradientBoosting, Voting)",
            "Usar validación cruzada estratificada",
            "Optimizar hiperparámetros con GridSearchCV",
            "Considerar modelos más complejos (XGBoost, LightGBM)"
        ])
        
        recommendations['data_collection'].extend([
            "Recolectar más datos para clases minoritarias",
            "Mejorar la calidad de las respuestas del formulario vocacional",
            "Incluir más variables predictoras relevantes"
        ])
        
        # Imprimir recomendaciones
        for category, recs in recommendations.items():
            if recs:
                print(f"\n{category.upper()}:")
                for i, rec in enumerate(recs, 1):
                    print(f"  {i}. {rec}")
        
        self.analysis_results['recommendations'] = recommendations
        return recommendations
    
    def run_full_analysis(self) -> Dict:
        """
        Ejecutar análisis completo de calidad de datos
        """
        print("=== ANÁLISIS COMPLETO DE CALIDAD DE DATOS ===")
        
        # Cargar datos
        self.load_data()
        
        # Ejecutar análisis
        self.analyze_missing_data()
        self.analyze_target_distribution()
        self.analyze_feature_correlations()
        self.analyze_feature_importance_estimate()
        self.analyze_data_quality_issues()
        self.generate_improvement_recommendations()
        
        print("\n=== ANÁLISIS COMPLETADO ===")
        return self.analysis_results


def main():
    """
    Función principal
    """
    analyzer = DataQualityAnalyzer()
    results = analyzer.run_full_analysis()
    
    print("\n" + "="*60)
    print("RESUMEN DEL ANÁLISIS")
    print("="*60)
    
    # Estadísticas básicas
    print(f"Total de registros: {len(analyzer.df)}")
    print(f"Total de características: {len(analyzer.df.columns)}")
    
    # Problemas identificados
    if 'quality_issues' in results:
        print(f"Problemas de calidad identificados: {len(results['quality_issues'])}")
    
    # Recomendaciones
    if 'recommendations' in results:
        total_recs = sum(len(recs) for recs in results['recommendations'].values())
        print(f"Recomendaciones generadas: {total_recs}")
    
    print("="*60)


if __name__ == "__main__":
    main() 