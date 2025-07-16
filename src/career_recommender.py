"""
Sistema de recomendación de carreras basado en perfiles vocacionales
"""

import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from career_database import CareerDatabase

class CareerRecommender:
    """
    Sistema de recomendación de carreras universitarias basado en perfiles vocacionales
    """
    
    def __init__(self, 
                 personality_model_path: str = "models/improved_vocacional_model_perfil_personalidad.pkl",
                 sector_model_path: str = "models/improved_vocacional_model_sector_preferido.pkl"):
        """
        Inicializa el sistema de recomendación
        
        Args:
            personality_model_path: Ruta al modelo de perfil de personalidad
            sector_model_path: Ruta al modelo de sector preferido
        """
        self.personality_model_path = personality_model_path
        self.sector_model_path = sector_model_path
        self.career_db = CareerDatabase()
        
        # Cargar modelos
        self.personality_model_data = self._load_model(personality_model_path)
        self.sector_model_data = self._load_model(sector_model_path)
        
        # Adaptar para modelos guardados como objeto directo
        if isinstance(self.personality_model_data, dict):
            self.personality_model = self.personality_model_data['model']
            self.personality_encoder = self.personality_model_data['label_encoder']
            self.personality_features = self.personality_model_data['feature_columns']
        else:
            self.personality_model = self.personality_model_data
            self.personality_encoder = None
            self.personality_features = None
        
        if isinstance(self.sector_model_data, dict):
            self.sector_model = self.sector_model_data['model']
            self.sector_encoder = self.sector_model_data['label_encoder']
            self.sector_features = self.sector_model_data['feature_columns']
        else:
            self.sector_model = self.sector_model_data
            self.sector_encoder = None
            self.sector_features = None
    
    def _load_model(self, model_path: str) -> Dict:
        """
        Carga un modelo entrenado
        """
        try:
            model_data = joblib.load(model_path)
            return model_data
        except Exception as e:
            print(f"Error cargando modelo {model_path}: {e}")
            return {}
    
    def predict_profile(self, student_data: Dict) -> Tuple[str, float]:
        """
        Predice el perfil de personalidad de un estudiante
        
        Args:
            student_data: Diccionario con datos del estudiante
            
        Returns:
            Tupla con (perfil_predicho, probabilidad)
        """
        # Preparar datos para predicción
        features = self._prepare_features(student_data, self.personality_features)
        
        # Hacer predicción
        prediction = self.personality_model.predict(features)[0]
        probabilities = self.personality_model.predict_proba(features)[0]
        
        # Decodificar resultado
        predicted_profile = self.personality_encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        
        return predicted_profile, confidence
    
    def predict_sector(self, student_data: Dict) -> Tuple[str, float]:
        """
        Predice el sector preferido de un estudiante
        
        Args:
            student_data: Diccionario con datos del estudiante
            
        Returns:
            Tupla con (sector_predicho, probabilidad)
        """
        # Preparar datos para predicción
        features = self._prepare_features(student_data, self.sector_features)
        
        # Hacer predicción
        prediction = self.sector_model.predict(features)[0]
        probabilities = self.sector_model.predict_proba(features)[0]
        
        # Decodificar resultado
        predicted_sector = self.sector_encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        
        return predicted_sector, confidence
    
    def _prepare_features(self, student_data: Dict, required_features: List[str]) -> np.ndarray:
        """
        Prepara las características del estudiante para la predicción
        """
        feature_values = []
        
        for feature in required_features:
            if feature in student_data:
                value = student_data[feature]
                
                # Manejar variables categóricas
                if isinstance(value, str):
                    # Mapear valores categóricos a números
                    if "Rendimiento" in feature:
                        mapping = {"Bajo": 0, "Medio": 1, "Alto": 2}
                        value = mapping.get(value, 1)  # Default: Medio
                    elif "Coherencia" in feature:
                        mapping = {"Poco Coherente": 0, "Coherente": 1, "Muy Coherente": 2}
                        value = mapping.get(value, 1)  # Default: Coherente
                
                feature_values.append(value)
            else:
                # Valor por defecto si no está disponible
                feature_values.append(3.0)  # Promedio neutral
        
        return np.array(feature_values).reshape(1, -1)
    
    def recommend_careers(self, student_data: Dict, top_n: int = 5) -> List[Dict]:
        """
        Recomienda carreras para un estudiante
        
        Args:
            student_data: Datos del estudiante
            top_n: Número de carreras a recomendar
            
        Returns:
            Lista de carreras recomendadas con información detallada
        """
        # Predecir perfil y sector
        predicted_profile, profile_confidence = self.predict_profile(student_data)
        predicted_sector, sector_confidence = self.predict_sector(student_data)
        
        print(f"Perfil predicho: {predicted_profile} (confianza: {profile_confidence:.3f})")
        print(f"Sector predicho: {predicted_sector} (confianza: {sector_confidence:.3f})")
        
        # Obtener carreras candidatas
        careers_by_profile = set(self.career_db.get_careers_by_profile(predicted_profile))
        careers_by_sector = set(self.career_db.get_careers_by_sector(predicted_sector))
        
        # Calcular puntuaciones para cada carrera
        career_scores = {}
        
        # Carreras que coinciden con ambos criterios (puntuación más alta)
        both_criteria = careers_by_profile.intersection(careers_by_sector)
        for career in both_criteria:
            career_scores[career] = self._calculate_career_score(
                career, student_data, predicted_profile, predicted_sector,
                profile_confidence, sector_confidence, match_both=True
            )
        
        # Carreras que coinciden solo con perfil
        profile_only = careers_by_profile - careers_by_sector
        for career in profile_only:
            career_scores[career] = self._calculate_career_score(
                career, student_data, predicted_profile, predicted_sector,
                profile_confidence, sector_confidence, match_both=False
            )
        
        # Carreras que coinciden solo con sector
        sector_only = careers_by_sector - careers_by_profile
        for career in sector_only:
            career_scores[career] = self._calculate_career_score(
                career, student_data, predicted_profile, predicted_sector,
                profile_confidence, sector_confidence, match_both=False
            )
        
        # Ordenar por puntuación
        sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Preparar recomendaciones
        recommendations = []
        for career_name, score in sorted_careers[:top_n]:
            career_info = self.career_db.get_career_info(career_name)
            
            recommendation = {
                'nombre': career_name,
                'puntuacion': score,
                'descripcion': career_info.get('descripcion', ''),
                'duracion': career_info.get('duracion', ''),
                'modalidad': career_info.get('modalidad', []),
                'universidades': career_info.get('universidades', [])[:3],  # Top 3
                'campo_laboral': career_info.get('campo_laboral', []),
                'salario_promedio': career_info.get('salario_promedio', ''),
                'requisitos_academicos': career_info.get('requisitos_academicos', {}),
                'match_perfil': career_name in careers_by_profile,
                'match_sector': career_name in careers_by_sector,
                'perfil_predicho': predicted_profile,
                'sector_predicho': predicted_sector
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_career_score(self, career_name: str, student_data: Dict, 
                              predicted_profile: str, predicted_sector: str,
                              profile_confidence: float, sector_confidence: float,
                              match_both: bool = False) -> float:
        """
        Calcula la puntuación de una carrera para un estudiante
        """
        career_info = self.career_db.get_career_info(career_name)
        
        # Puntuación base
        base_score = 0.5
        
        # Bonificación por coincidencia de perfil y sector
        if match_both:
            base_score += 0.3
        else:
            base_score += 0.15
        
        # Bonificación por confianza en las predicciones
        confidence_bonus = (profile_confidence + sector_confidence) / 2 * 0.2
        base_score += confidence_bonus
        
        # Bonificación por requisitos académicos
        academic_bonus = self._calculate_academic_match(career_info, student_data)
        base_score += academic_bonus
        
        return min(base_score, 1.0)  # Máximo 1.0
    
    def _calculate_academic_match(self, career_info: Dict, student_data: Dict) -> float:
        """
        Calcula qué tan bien coinciden los requisitos académicos
        """
        if 'requisitos_academicos' not in career_info:
            return 0.0
        
        requirements = career_info['requisitos_academicos']
        match_score = 0.0
        total_requirements = len(requirements)
        
        if total_requirements == 0:
            return 0.0
        
        for subject, required_level in requirements.items():
            # Mapear nombres de materias
            subject_mapping = {
                'matematicas': 'Matemáticas - Promedio',
                'fisica': 'Física - Promedio',
                'biologia': 'Biología y química - Promedio',
                'quimica': 'Biología y química - Promedio',
                'ciencias_sociales': 'Ciencias sociales - Promedio',
                'lengua_castellana': 'Lengua castellana - Promedio',
                'ciencias_economicas': 'Ciencias económicas y políticas - Promedio',
                'educacion_artistica': 'Educación artística - Promedio',
                'educacion_fisica': 'Educación física - Promedio'
            }
            
            mapped_subject = subject_mapping.get(subject, subject)
            
            if mapped_subject in student_data:
                student_grade = student_data[mapped_subject]
                
                # Evaluar si cumple el requisito
                if required_level == "Alto" and student_grade >= 4.0:
                    match_score += 1.0
                elif required_level == "Medio" and student_grade >= 3.0:
                    match_score += 1.0
                elif required_level == "Bajo" and student_grade >= 2.0:
                    match_score += 1.0
                else:
                    # Puntuación parcial basada en qué tan cerca está
                    if required_level == "Alto":
                        match_score += max(0, (student_grade - 2.0) / 2.0)
                    elif required_level == "Medio":
                        match_score += max(0, (student_grade - 1.0) / 2.0)
        
        return (match_score / total_requirements) * 0.15  # Máximo 15% de bonificación
    
    def generate_recommendation_report(self, student_data: Dict, 
                                     recommendations: List[Dict]) -> str:
        """
        Genera un reporte detallado de recomendaciones
        """
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE RECOMENDACIONES VOCACIONALES")
        report.append("=" * 60)
        
        # Información del estudiante
        student_name = student_data.get('Nombre completo', 'Estudiante')
        report.append(f"Estudiante: {student_name}")
        report.append(f"Promedio General: {student_data.get('Promedio General', 'N/A')}")
        
        if recommendations:
            predicted_profile = recommendations[0]['perfil_predicho']
            predicted_sector = recommendations[0]['sector_predicho']
            report.append(f"Perfil de Personalidad: {predicted_profile}")
            report.append(f"Sector Preferido: {predicted_sector}")
        
        report.append("\n" + "=" * 60)
        report.append("CARRERAS RECOMENDADAS")
        report.append("=" * 60)
        
        for i, rec in enumerate(recommendations, 1):
            report.append(f"\n{i}. {rec['nombre']}")
            report.append(f"   Puntuación: {rec['puntuacion']:.3f}")
            report.append(f"   Descripción: {rec['descripcion']}")
            report.append(f"   Duración: {rec['duracion']}")
            report.append(f"   Modalidad: {', '.join(rec['modalidad'])}")
            report.append(f"   Salario Promedio: {rec['salario_promedio']}")
            
            # Coincidencias
            matches = []
            if rec['match_perfil']:
                matches.append("Perfil")
            if rec['match_sector']:
                matches.append("Sector")
            report.append(f"   Coincide con: {', '.join(matches)}")
            
            # Universidades
            if rec['universidades']:
                report.append(f"   Universidades recomendadas:")
                for uni in rec['universidades']:
                    report.append(f"     - {uni}")
            
            # Campo laboral
            if rec['campo_laboral']:
                report.append(f"   Oportunidades laborales:")
                for oportunidad in rec['campo_laboral'][:3]:
                    report.append(f"     - {oportunidad}")
        
        report.append("\n" + "=" * 60)
        report.append("RECOMENDACIONES ADICIONALES")
        report.append("=" * 60)
        report.append("1. Investiga más sobre las carreras que te interesan")
        report.append("2. Habla con profesionales en esas áreas")
        report.append("3. Considera hacer prácticas o voluntariados")
        report.append("4. Visita las universidades que te interesan")
        report.append("5. Consulta con un orientador vocacional")
        
        return "\n".join(report)


def main():
    """
    Función principal para probar el sistema de recomendación
    """
    print("=== SISTEMA DE RECOMENDACIÓN VOCACIONAL ===")
    
    # Crear instancia del recomendador
    try:
        recommender = CareerRecommender()
        print("✅ Sistema de recomendación inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando el sistema: {e}")
        return
    
    # Datos de ejemplo de un estudiante
    student_example = {
        'Nombre completo': 'Estudiante Ejemplo',
        'Física - Promedio': 4.2,
        'Biología y química - Promedio': 3.8,
        'Educación artística - Promedio': 3.0,
        'Ciencias sociales - Promedio': 3.5,
        'Educación física - Promedio': 3.2,
        'Matemáticas - Promedio': 4.5,
        'Lengua castellana - Promedio': 3.7,
        'Ciencias económicas y políticas - Promedio': 3.3,
        'Promedio General': 3.65,
        'Cantidad Materias Favoritas': 3,
        'Cantidad Materias No Favoritas': 3,
        'Cantidad Materias Buenas': 3,
        'Cantidad Materias Malas': 3,
        'Rendimiento General': 'Medio',
        'Coherencia Gustos-Rendimiento': 'Coherente'
    }
    
    # Generar recomendaciones
    print("\n=== GENERANDO RECOMENDACIONES ===")
    recommendations = recommender.recommend_careers(student_example, top_n=5)
    
    # Mostrar reporte
    report = recommender.generate_recommendation_report(student_example, recommendations)
    print("\n" + report)


if __name__ == "__main__":
    main() 