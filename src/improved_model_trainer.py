import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
import os
from typing import Tuple, Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

class ImprovedVocacionalModelTrainer:
    """
    Entrenador mejorado de modelos vocacionales con técnicas avanzadas
    """
    
    def __init__(self, data_path: str = "data/dataset_completo.csv"):
        """
        Inicializa el entrenador mejorado
        
        Args:
            data_path: Ruta al archivo CSV con los datos procesados
        """
        self.data_path = data_path
        self.df = None
        self.X = None
        self.y = None
        self.label_encoder = LabelEncoder()
        self.scaler = None
        self.best_model = None
        self.feature_selector = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Cargar y limpiar los datos
        """
        print("Cargando y limpiando dataset...")
        self.df = pd.read_csv(self.data_path, encoding='utf-8')
        
        # Limpiar datos
        self.df = self.df.dropna(subset=['Perfil Personalidad', 'Sector Preferido'])
        
        print(f"Dataset cargado: {len(self.df)} estudiantes, {len(self.df.columns)} columnas")
        return self.df
    
    def engineer_features(self) -> pd.DataFrame:
        """
        Ingeniería de características avanzada
        """
        print("Realizando ingeniería de características...")
        
        # Crear características derivadas
        df_engineered = self.df.copy()
        
        # 1. Ratios de rendimiento
        df_engineered['ratio_matematicas_ciencias'] = (
            df_engineered['Matemáticas - Promedio'] / 
            df_engineered['Biología y química - Promedio']
        ).fillna(1.0)
        
        df_engineered['ratio_ciencias_sociales'] = (
            df_engineered['Biología y química - Promedio'] / 
            df_engineered['Ciencias sociales - Promedio']
        ).fillna(1.0)
        
        # 2. Variabilidad en notas
        materias = ['Física - Promedio', 'Biología y química - Promedio', 
                   'Educación artística - Promedio', 'Ciencias sociales - Promedio',
                   'Educación física - Promedio', 'Matemáticas - Promedio',
                   'Lengua castellana - Promedio', 'Ciencias económicas y políticas - Promedio']
        
        df_engineered['std_notas'] = df_engineered[materias].std(axis=1)
        df_engineered['range_notas'] = df_engineered[materias].max(axis=1) - df_engineered[materias].min(axis=1)
        
        # 3. Perfil de fortalezas
        df_engineered['fortaleza_cientifica'] = (
            df_engineered['Matemáticas - Promedio'] + 
            df_engineered['Física - Promedio'] + 
            df_engineered['Biología y química - Promedio']
        ) / 3
        
        df_engineered['fortaleza_humanistica'] = (
            df_engineered['Ciencias sociales - Promedio'] + 
            df_engineered['Lengua castellana - Promedio'] + 
            df_engineered['Ciencias económicas y políticas - Promedio']
        ) / 3
        
        df_engineered['fortaleza_artistica'] = (
            df_engineered['Educación artística - Promedio'] + 
            df_engineered['Educación física - Promedio']
        ) / 2
        
        # 4. Balance académico
        df_engineered['balance_academico'] = abs(
            df_engineered['fortaleza_cientifica'] - df_engineered['fortaleza_humanistica']
        )
        
        # 5. Coherencia mejorada
        coherencia_mapping = {
            'Muy Coherente': 3,
            'Coherente': 2,
            'Poco Coherente': 1
        }
        df_engineered['coherencia_numerica'] = df_engineered['Coherencia Gustos-Rendimiento'].map(coherencia_mapping)
        
        # 6. Perfil de rendimiento
        df_engineered['rendimiento_alto_count'] = (df_engineered[materias] >= 4.0).sum(axis=1)
        df_engineered['rendimiento_medio_count'] = ((df_engineered[materias] >= 3.0) & (df_engineered[materias] < 4.0)).sum(axis=1)
        df_engineered['rendimiento_bajo_count'] = (df_engineered[materias] < 3.0).sum(axis=1)
        
        self.df = df_engineered
        print(f"Características adicionales creadas: {len(df_engineered.columns) - len(self.df.columns)} nuevas features")
        
        return self.df
    
    def select_features(self, target_variable: str = "Perfil Personalidad") -> Tuple[pd.DataFrame, pd.Series]:
        """
        Selección avanzada de características
        """
        print(f"Seleccionando features para predecir: {target_variable}")
        
        # Características numéricas base
        numeric_features = [
            'Física - Promedio', 'Biología y química - Promedio', 'Educación artística - Promedio',
            'Ciencias sociales - Promedio', 'Educación física - Promedio', 'Matemáticas - Promedio',
            'Lengua castellana - Promedio', 'Ciencias económicas y políticas - Promedio',
            'Promedio General', 'Cantidad Materias Favoritas', 'Cantidad Materias No Favoritas',
            'Cantidad Materias Buenas', 'Cantidad Materias Malas'
        ]
        
        # Características categóricas
        categorical_features = [
            'Rendimiento General', 'Física - Rendimiento', 'Biología y química - Rendimiento',
            'Educación artística - Rendimiento', 'Ciencias sociales - Rendimiento',
            'Educación física - Rendimiento', 'Matemáticas - Rendimiento',
            'Lengua castellana - Rendimiento', 'Ciencias económicas y políticas - Rendimiento',
            'Coherencia Gustos-Rendimiento'
        ]
        
        # Características derivadas (nuevas)
        derived_features = [
            'ratio_matematicas_ciencias', 'ratio_ciencias_sociales', 'std_notas', 'range_notas',
            'fortaleza_cientifica', 'fortaleza_humanistica', 'fortaleza_artistica',
            'balance_academico', 'coherencia_numerica', 'rendimiento_alto_count',
            'rendimiento_medio_count', 'rendimiento_bajo_count'
        ]
        
        # Verificar disponibilidad
        available_numeric = [col for col in numeric_features if col in self.df.columns]
        available_categorical = [col for col in categorical_features if col in self.df.columns]
        available_derived = [col for col in derived_features if col in self.df.columns]
        
        print(f"Features numéricas: {len(available_numeric)}")
        print(f"Features categóricas: {len(available_categorical)}")
        print(f"Features derivadas: {len(available_derived)}")
        
        # Combinar todas las características
        feature_columns = available_numeric + available_categorical + available_derived
        self.X = self.df[feature_columns].copy()
        
        # Verificar variable objetivo
        if target_variable not in self.df.columns:
            raise ValueError(f"La variable objetivo '{target_variable}' no existe en el dataset")
        
        self.y = self.df[target_variable].copy()
        
        print(f"Total de features seleccionadas: {len(feature_columns)}")
        print(f"Distribución de la variable objetivo:")
        print(self.y.value_counts())
        
        return self.X, self.y
    
    def encode_categorical_features(self) -> pd.DataFrame:
        """
        Codificación avanzada de características categóricas
        """
        print("Codificando variables categóricas...")
        
        categorical_columns = self.X.select_dtypes(include=['object']).columns
        
        if len(categorical_columns) > 0:
            print(f"Codificando {len(categorical_columns)} columnas categóricas...")
            
            for col in categorical_columns:
                # Manejar valores nulos
                self.X[col] = self.X[col].fillna('Desconocido')
                
                # Aplicar LabelEncoder
                le = LabelEncoder()
                self.X[col] = le.fit_transform(self.X[col].astype(str))
                print(f"  - {col}: {len(le.classes_)} categorías")
        else:
            print("No hay columnas categóricas para codificar")
        
        return self.X
    
    def encode_target_variable(self) -> pd.Series:
        """
        Codificar variable objetivo
        """
        print("Codificando variable objetivo...")
        
        if self.y.dtype == 'object':
            # Manejar valores nulos
            self.y = self.y.fillna('Desconocido')
            self.y = self.label_encoder.fit_transform(self.y)
            print(f"Variable objetivo codificada: {len(self.label_encoder.classes_)} categorías")
            print("Categorías:", list(self.label_encoder.classes_))
        else:
            print("La variable objetivo ya es numérica")
        
        return self.y
    
    def split_data(self, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        División estratificada de datos
        """
        print(f"Dividiendo datos: {test_size*100}% para prueba")
        
        # Verificar distribución de clases
        unique, counts = np.unique(self.y, return_counts=True)
        print(f"Distribución de clases:")
        for class_idx, count in zip(unique, counts):
            if hasattr(self.label_encoder, 'classes_') and class_idx < len(self.label_encoder.classes_):
                class_name = self.label_encoder.classes_[class_idx]
            else:
                class_name = f"Clase {class_idx}"
            print(f"  - {class_name}: {count} muestras")
        
        # División estratificada
        try:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                self.X, self.y, test_size=test_size, random_state=random_state, stratify=self.y
            )
            print("✅ División estratificada exitosa")
        except ValueError as e:
            print(f"⚠️  No se pudo hacer división estratificada: {e}")
            print("Usando división simple...")
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                self.X, self.y, test_size=test_size, random_state=random_state
            )
        
        print(f"Conjunto de entrenamiento: {len(self.X_train)} muestras")
        print(f"Conjunto de prueba: {len(self.X_test)} muestras")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def feature_selection(self) -> pd.DataFrame:
        """
        Selección de características más importantes
        """
        print("Realizando selección de características...")
        
        # Usar SelectKBest para seleccionar las mejores características
        k = min(20, len(self.X_train.columns))  # Máximo 20 características
        selector = SelectKBest(score_func=f_classif, k=k)
        
        X_train_selected = selector.fit_transform(self.X_train, self.y_train)
        X_test_selected = selector.transform(self.X_test)
        
        # Obtener nombres de características seleccionadas
        selected_features = self.X_train.columns[selector.get_support()].tolist()
        
        print(f"Características seleccionadas: {len(selected_features)}")
        print("Top 10 características más importantes:")
        
        # Mostrar scores de características
        scores = selector.scores_
        feature_scores = list(zip(self.X_train.columns, scores))
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        
        for i, (feature, score) in enumerate(feature_scores[:10]):
            print(f"  {i+1}. {feature}: {score:.4f}")
        
        # Actualizar datos con características seleccionadas
        self.X_train = pd.DataFrame(X_train_selected, columns=selected_features)
        self.X_test = pd.DataFrame(X_test_selected, columns=selected_features)
        self.X = pd.concat([self.X_train, self.X_test], ignore_index=True)
        
        self.feature_selector = selector
        return self.X_train
    
    def scale_features(self) -> pd.DataFrame:
        """
        Escalado de características
        """
        print("Escalando características...")
        
        # Usar RobustScaler para manejar outliers
        self.scaler = RobustScaler()
        
        X_train_scaled = self.scaler.fit_transform(self.X_train)
        X_test_scaled = self.scaler.transform(self.X_test)
        
        # Convertir de vuelta a DataFrame
        self.X_train = pd.DataFrame(X_train_scaled, columns=self.X_train.columns)
        self.X_test = pd.DataFrame(X_test_scaled, columns=self.X_test.columns)
        
        print("Características escaladas exitosamente")
        return self.X_train
    
    def train_ensemble_model(self) -> VotingClassifier:
        """
        Entrenar modelo ensemble para mejor precisión
        """
        print("Entrenando modelo ensemble...")
        
        # Definir modelos base
        rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
        lr = LogisticRegression(max_iter=1000, random_state=42)
        svm = SVC(probability=True, random_state=42)
        
        # Crear ensemble
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf),
                ('gb', gb),
                ('lr', lr),
                ('svm', svm)
            ],
            voting='soft'  # Usar probabilidades
        )
        
        # Entrenar ensemble
        ensemble.fit(self.X_train, self.y_train)
        
        self.best_model = ensemble
        print("Modelo ensemble entrenado exitosamente")
        
        return ensemble
    
    def hyperparameter_tuning(self) -> RandomForestClassifier:
        """
        Optimización de hiperparámetros
        """
        print("Realizando optimización de hiperparámetros...")
        
        # Definir parámetros para búsqueda
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        }
        
        # Usar validación cruzada estratificada
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        # Búsqueda de hiperparámetros
        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(
            rf, param_grid, cv=cv, scoring='accuracy', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(self.X_train, self.y_train)
        
        print(f"Mejores parámetros: {grid_search.best_params_}")
        print(f"Mejor score CV: {grid_search.best_score_:.4f}")
        
        self.best_model = grid_search.best_estimator_
        return self.best_model
    
    def evaluate_model(self) -> Dict[str, Any]:
        """
        Evaluación completa del modelo
        """
        print("Evaluando modelo...")
        
        # Predicciones
        y_pred = self.best_model.predict(self.X_test)
        y_pred_proba = self.best_model.predict_proba(self.X_test)
        
        # Métricas básicas
        accuracy = accuracy_score(self.y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(self.y_test, y_pred, average='weighted')
        
        # Validación cruzada
        cv_scores = cross_val_score(self.best_model, self.X_train, self.y_train, cv=5, scoring='accuracy')
        
        # Reporte de clasificación
        if hasattr(self.label_encoder, 'classes_'):
            target_names = list(self.label_encoder.classes_)
        else:
            target_names = None
        
        try:
            classification_rep = classification_report(
                self.y_test, y_pred, 
                target_names=target_names,
                output_dict=True,
                zero_division=0
            )
        except Exception as e:
            print(f"⚠️  Error en reporte de clasificación: {e}")
            classification_rep = {}
        
        # Matriz de confusión
        conf_matrix = confusion_matrix(self.y_test, y_pred)
        
        # Resultados
        results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'classification_report': classification_rep,
            'confusion_matrix': conf_matrix,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
        
        # Imprimir resultados
        print(f"\n=== RESULTADOS DE EVALUACIÓN MEJORADA ===")
        print(f"Precisión (Accuracy): {accuracy:.4f}")
        print(f"Precisión (Precision): {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print(f"CV Accuracy (mean ± std): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        try:
            print(f"\nReporte de clasificación:")
            print(classification_report(self.y_test, y_pred, target_names=target_names, zero_division=0))
        except Exception as e:
            print(f"⚠️  No se pudo generar reporte de clasificación completo: {e}")
        
        print(f"\nMatriz de confusión:")
        print(conf_matrix)
        
        return results
    
    def save_model(self, model_path: str = "models/improved_vocacional_model.pkl") -> None:
        """
        Guardar modelo mejorado
        """
        print(f"Guardando modelo mejorado en: {model_path}")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Guardar modelo y componentes
        model_data = {
            'model': self.best_model,
            'label_encoder': self.label_encoder,
            'scaler': self.scaler,
            'feature_selector': self.feature_selector,
            'feature_columns': list(self.X_train.columns),
            'target_variable': self.y.name if hasattr(self.y, 'name') else 'target'
        }
        
        joblib.dump(model_data, model_path)
        print("Modelo mejorado guardado exitosamente")
    
    def run_improved_training(self, target_variable: str = "Perfil Personalidad", 
                             test_size: float = 0.2, 
                             save_model: bool = True) -> Dict[str, Any]:
        """
        Ejecuta el entrenamiento mejorado completo
        """
        print("=== INICIANDO ENTRENAMIENTO MEJORADO ===")
        
        # Cargar y limpiar datos
        self.load_data()
        
        # Ingeniería de características
        self.engineer_features()
        
        # Seleccionar características
        self.select_features(target_variable)
        
        # Codificar variables
        self.encode_categorical_features()
        self.encode_target_variable()
        
        # Dividir datos
        self.split_data(test_size=test_size)
        
        # Selección de características
        self.feature_selection()
        
        # Escalado
        self.scale_features()
        
        # Entrenar modelo (elegir entre ensemble o tuning)
        print("\n¿Qué tipo de modelo prefieres?")
        print("1. Ensemble (más rápido)")
        print("2. Optimización de hiperparámetros (más preciso pero más lento)")
        
        choice = input("Elige una opción (1 o 2): ").strip()
        
        if choice == "2":
            self.hyperparameter_tuning()
        else:
            self.train_ensemble_model()
        
        # Evaluar modelo
        results = self.evaluate_model()
        
        # Guardar modelo
        if save_model:
            model_path = f"models/improved_vocacional_model_{target_variable.lower().replace(' ', '_')}.pkl"
            self.save_model(model_path)
        
        print("=== ENTRENAMIENTO MEJORADO COMPLETADO ===")
        
        return results


def main():
    """
    Función principal para ejecutar el entrenamiento mejorado
    """
    # Crear instancia del entrenador mejorado
    trainer = ImprovedVocacionalModelTrainer()
    
    # Entrenar modelo para Perfil Personalidad
    print("\n" + "="*60)
    print("ENTRENANDO MODELO MEJORADO PARA PERFIL PERSONALIDAD")
    print("="*60)
    
    results_personalidad = trainer.run_improved_training(
        target_variable="Perfil Personalidad",
        test_size=0.2,
        save_model=True
    )
    
    # Entrenar modelo para Sector Preferido
    print("\n" + "="*60)
    print("ENTRENANDO MODELO MEJORADO PARA SECTOR PREFERIDO")
    print("="*60)
    
    trainer_sector = ImprovedVocacionalModelTrainer()
    results_sector = trainer_sector.run_improved_training(
        target_variable="Sector Preferido",
        test_size=0.2,
        save_model=True
    )
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL - MODELOS MEJORADOS")
    print("="*60)
    print(f"Modelo Perfil Personalidad:")
    print(f"  - Accuracy: {results_personalidad['accuracy']:.4f}")
    print(f"  - F1-Score: {results_personalidad['f1_score']:.4f}")
    print(f"  - CV Accuracy: {results_personalidad['cv_mean']:.4f} ± {results_personalidad['cv_std']:.4f}")
    
    print(f"\nModelo Sector Preferido:")
    print(f"  - Accuracy: {results_sector['accuracy']:.4f}")
    print(f"  - F1-Score: {results_sector['f1_score']:.4f}")
    print(f"  - CV Accuracy: {results_sector['cv_mean']:.4f} ± {results_sector['cv_std']:.4f}")
    print("="*60)


if __name__ == "__main__":
    main() 