import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.feature_selection import SelectKBest, f_classif
import joblib
import os
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class ModelComparison:
    """
    Comparador de diferentes modelos y técnicas para mejorar la precisión
    """
    
    def __init__(self, data_path: str = "data/dataset_completo.csv"):
        self.data_path = data_path
        self.df = None
        self.X = None
        self.y = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.results = {}
        
    def load_and_prepare_data(self, target_variable: str = "Perfil Personalidad") -> Tuple[pd.DataFrame, pd.Series]:
        """
        Cargar y preparar datos
        """
        print("Cargando y preparando datos...")
        
        # Cargar datos
        self.df = pd.read_csv(self.data_path, encoding='utf-8')
        self.df = self.df.dropna(subset=[target_variable])
        
        # Seleccionar características
        numeric_features = [
            'Física - Promedio', 'Biología y química - Promedio', 'Educación artística - Promedio',
            'Ciencias sociales - Promedio', 'Educación física - Promedio', 'Matemáticas - Promedio',
            'Lengua castellana - Promedio', 'Ciencias económicas y políticas - Promedio',
            'Promedio General', 'Cantidad Materias Favoritas', 'Cantidad Materias No Favoritas',
            'Cantidad Materias Buenas', 'Cantidad Materias Malas'
        ]
        
        categorical_features = [
            'Rendimiento General', 'Física - Rendimiento', 'Biología y química - Rendimiento',
            'Educación artística - Rendimiento', 'Ciencias sociales - Rendimiento',
            'Educación física - Rendimiento', 'Matemáticas - Rendimiento',
            'Lengua castellana - Rendimiento', 'Ciencias económicas y políticas - Rendimiento',
            'Coherencia Gustos-Rendimiento'
        ]
        
        # Verificar disponibilidad
        available_numeric = [col for col in numeric_features if col in self.df.columns]
        available_categorical = [col for col in categorical_features if col in self.df.columns]
        
        feature_columns = available_numeric + available_categorical
        self.X = self.df[feature_columns].copy()
        self.y = self.df[target_variable].copy()
        
        # Codificar variables categóricas
        categorical_columns = self.X.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            le = LabelEncoder()
            self.X[col] = le.fit_transform(self.X[col].fillna('Desconocido').astype(str))
        
        # Codificar variable objetivo
        self.y = self.label_encoder.fit_transform(self.y.fillna('Desconocido'))
        
        print(f"Datos preparados: {len(self.X)} muestras, {len(self.X.columns)} características")
        print(f"Distribución de clases: {np.bincount(self.y)}")
        
        return self.X, self.y
    
    def compare_basic_models(self) -> Dict:
        """
        Comparar modelos básicos
        """
        print("\n=== COMPARACIÓN DE MODELOS BÁSICOS ===")
        
        models = {
            'Decision Tree': DecisionTreeClassifier(random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'SVM': SVC(probability=True, random_state=42)
        }
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        results = {}
        
        for name, model in models.items():
            print(f"Evaluando {name}...")
            
            # Validación cruzada
            cv_scores = cross_val_score(model, self.X, self.y, cv=cv, scoring='accuracy')
            
            # Entrenar modelo completo para métricas adicionales
            model.fit(self.X, self.y)
            y_pred = model.predict(self.X)
            
            # Métricas
            accuracy = accuracy_score(self.y, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(self.y, y_pred, average='weighted')
            
            results[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
            
            print(f"  CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            print(f"  F1-Score: {f1:.4f}")
        
        # Mostrar ranking
        print("\nRanking de modelos básicos (por CV Accuracy):")
        sorted_results = sorted(results.items(), key=lambda x: x[1]['cv_mean'], reverse=True)
        for i, (name, metrics) in enumerate(sorted_results, 1):
            print(f"  {i}. {name}: {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
        
        self.results['basic_models'] = results
        return results
    
    def compare_ensemble_methods(self) -> Dict:
        """
        Comparar métodos ensemble
        """
        print("\n=== COMPARACIÓN DE MÉTODOS ENSEMBLE ===")
        
        # Modelos base
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        lr = LogisticRegression(max_iter=1000, random_state=42)
        svm = SVC(probability=True, random_state=42)
        
        ensembles = {
            'Voting (Hard)': VotingClassifier(
                estimators=[('rf', rf), ('gb', gb), ('lr', lr)],
                voting='hard'
            ),
            'Voting (Soft)': VotingClassifier(
                estimators=[('rf', rf), ('gb', gb), ('lr', lr)],
                voting='soft'
            ),
            'Voting (All)': VotingClassifier(
                estimators=[('rf', rf), ('gb', gb), ('lr', lr), ('svm', svm)],
                voting='soft'
            )
        }
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        results = {}
        
        for name, ensemble in ensembles.items():
            print(f"Evaluando {name}...")
            
            # Validación cruzada
            cv_scores = cross_val_score(ensemble, self.X, self.y, cv=cv, scoring='accuracy')
            
            # Entrenar modelo completo
            ensemble.fit(self.X, self.y)
            y_pred = ensemble.predict(self.X)
            
            # Métricas
            accuracy = accuracy_score(self.y, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(self.y, y_pred, average='weighted')
            
            results[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
            
            print(f"  CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            print(f"  F1-Score: {f1:.4f}")
        
        # Mostrar ranking
        print("\nRanking de ensembles (por CV Accuracy):")
        sorted_results = sorted(results.items(), key=lambda x: x[1]['cv_mean'], reverse=True)
        for i, (name, metrics) in enumerate(sorted_results, 1):
            print(f"  {i}. {name}: {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
        
        self.results['ensemble_methods'] = results
        return results
    
    def compare_feature_selection_methods(self) -> Dict:
        """
        Comparar métodos de selección de características
        """
        print("\n=== COMPARACIÓN DE SELECCIÓN DE CARACTERÍSTICAS ===")
        
        # Modelo base
        base_model = RandomForestClassifier(n_estimators=100, random_state=42)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        # Diferentes números de características
        k_values = [5, 10, 15, 20, len(self.X.columns)]
        results = {}
        
        for k in k_values:
            if k > len(self.X.columns):
                continue
                
            print(f"Evaluando con {k} características...")
            
            # Selección de características
            selector = SelectKBest(score_func=f_classif, k=k)
            X_selected = selector.fit_transform(self.X, self.y)
            
            # Validación cruzada
            cv_scores = cross_val_score(base_model, X_selected, self.y, cv=cv, scoring='accuracy')
            
            # Entrenar modelo completo
            base_model.fit(X_selected, self.y)
            y_pred = base_model.predict(X_selected)
            
            # Métricas
            accuracy = accuracy_score(self.y, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(self.y, y_pred, average='weighted')
            
            results[f'{k}_features'] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'selected_features': k
            }
            
            print(f"  CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            print(f"  F1-Score: {f1:.4f}")
        
        # Mostrar ranking
        print("\nRanking de selección de características (por CV Accuracy):")
        sorted_results = sorted(results.items(), key=lambda x: x[1]['cv_mean'], reverse=True)
        for i, (name, metrics) in enumerate(sorted_results, 1):
            print(f"  {i}. {name}: {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
        
        self.results['feature_selection'] = results
        return results
    
    def compare_scaling_methods(self) -> Dict:
        """
        Comparar métodos de escalado
        """
        print("\n=== COMPARACIÓN DE MÉTODOS DE ESCALADO ===")
        
        from sklearn.preprocessing import MinMaxScaler, RobustScaler
        
        scalers = {
            'Sin escalado': None,
            'StandardScaler': StandardScaler(),
            'MinMaxScaler': MinMaxScaler(),
            'RobustScaler': RobustScaler()
        }
        
        # Modelo base
        base_model = RandomForestClassifier(n_estimators=100, random_state=42)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        results = {}
        
        for name, scaler in scalers.items():
            print(f"Evaluando {name}...")
            
            if scaler is None:
                X_scaled = self.X
            else:
                X_scaled = scaler.fit_transform(self.X)
            
            # Validación cruzada
            cv_scores = cross_val_score(base_model, X_scaled, self.y, cv=cv, scoring='accuracy')
            
            # Entrenar modelo completo
            base_model.fit(X_scaled, self.y)
            y_pred = base_model.predict(X_scaled)
            
            # Métricas
            accuracy = accuracy_score(self.y, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(self.y, y_pred, average='weighted')
            
            results[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
            
            print(f"  CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            print(f"  F1-Score: {f1:.4f}")
        
        # Mostrar ranking
        print("\nRanking de métodos de escalado (por CV Accuracy):")
        sorted_results = sorted(results.items(), key=lambda x: x[1]['cv_mean'], reverse=True)
        for i, (name, metrics) in enumerate(sorted_results, 1):
            print(f"  {i}. {name}: {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
        
        self.results['scaling_methods'] = results
        return results
    
    def run_comprehensive_comparison(self, target_variable: str = "Perfil Personalidad") -> Dict:
        """
        Ejecutar comparación completa
        """
        print("=== COMPARACIÓN COMPLETA DE MODELOS ===")
        
        # Preparar datos
        self.load_and_prepare_data(target_variable)
        
        # Ejecutar comparaciones
        self.compare_basic_models()
        self.compare_ensemble_methods()
        self.compare_feature_selection_methods()
        self.compare_scaling_methods()
        
        # Resumen final
        self.generate_final_summary()
        
        return self.results
    
    def generate_final_summary(self):
        """
        Generar resumen final de todas las comparaciones
        """
        print("\n" + "="*60)
        print("RESUMEN FINAL DE COMPARACIÓN")
        print("="*60)
        
        all_results = []
        
        # Recopilar todos los resultados
        for category, results in self.results.items():
            for model_name, metrics in results.items():
                all_results.append({
                    'category': category,
                    'model': model_name,
                    'cv_mean': metrics['cv_mean'],
                    'cv_std': metrics['cv_std'],
                    'f1_score': metrics['f1_score']
                })
        
        # Ordenar por CV mean
        all_results.sort(key=lambda x: x['cv_mean'], reverse=True)
        
        print("Top 10 mejores configuraciones:")
        for i, result in enumerate(all_results[:10], 1):
            print(f"  {i}. {result['category']} - {result['model']}: {result['cv_mean']:.4f} ± {result['cv_std']:.4f}")
        
        # Mejor resultado general
        best_result = all_results[0]
        print(f"\n🏆 MEJOR CONFIGURACIÓN:")
        print(f"  Categoría: {best_result['category']}")
        print(f"  Modelo: {best_result['model']}")
        print(f"  CV Accuracy: {best_result['cv_mean']:.4f} ± {best_result['cv_std']:.4f}")
        print(f"  F1-Score: {best_result['f1_score']:.4f}")
        
        print("="*60)


def main():
    """
    Función principal
    """
    # Comparar para Perfil Personalidad
    print("COMPARACIÓN PARA PERFIL PERSONALIDAD")
    print("="*60)
    
    comparator_personalidad = ModelComparison()
    results_personalidad = comparator_personalidad.run_comprehensive_comparison("Perfil Personalidad")
    
    # Comparar para Sector Preferido
    print("\n\nCOMPARACIÓN PARA SECTOR PREFERIDO")
    print("="*60)
    
    comparator_sector = ModelComparison()
    results_sector = comparator_sector.run_comprehensive_comparison("Sector Preferido")
    
    print("\n" + "="*60)
    print("COMPARACIÓN COMPLETADA")
    print("="*60)


if __name__ == "__main__":
    main() 