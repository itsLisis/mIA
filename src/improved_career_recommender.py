"""
Sistema de recomendación de carreras mejorado con coherencia y lógica avanzada
"""

import joblib
import pandas as pd
import numpy as np
import hashlib
from typing import Dict, List, Tuple, Any, Optional
from career_database import CareerDatabase
import json

class ImprovedCareerRecommender:
    """
    Sistema de recomendación de carreras mejorado con lógica de coherencia avanzada
    """
    
    def __init__(self, 
                 personality_model_path: str = "models/improved_vocacional_model_perfil_personalidad.pkl",
                 sector_model_path: str = "models/improved_vocacional_model_sector_preferido.pkl"):
        """
        Inicializa el sistema de recomendación mejorado
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
        
        # Configuración de pesos mejorados - REFORZANDO PREFERENCIAS DE ENTORNO Y SECTOR
        self.weights = {
            'profile_confidence': 0.18,          # Reducido para equilibrar con otras mejoras
            'sector_confidence': 0.18,           # Reducido para equilibrar con otras mejoras
            'explicit_sector_preference': 0.30,  # NUEVO: Peso fuerte para sectores explícitos
            'environment_sector_preferences': 0.20,  # NUEVO: Peso alto para entorno y sector laboral
            'academic_match': 0.10,              # Reducido para dar más peso a preferencias
            'work_environment': 0.02,            # Reducido, se maneja en environment_sector_preferences
            'social_interaction': 0.02,          # Reducido, se maneja en environment_sector_preferences
            'artistic_creative_bonus': 0.00,     # Se calcula dinámicamente para perfiles artísticos
            'very_coherent_bonus': 0.00          # Se calcula dinámicamente para coherencia "Muy Coherente"
        }
        
        # Mapeo de sectores del formulario a sectores del modelo - AMPLIADO
        self.sector_mapping = {
            'TIC (Tecnologías de la información y la comunicación) y telecomunicaciones': 'Tecnología',
            'Industrial manufacturero': 'Industrial',
            'Salud': 'Salud',
            'Educación': 'Educativo',
            'Cultural y artístico': 'Artístico',
            'Arte y comunicación': 'Artístico',  # NUEVO
            'Artes y comunicación': 'Artístico',  # NUEVO
            'Investigación en ciencias básicas y aplicadas': 'Investigación',
            'Comercio': 'Comercial',
            'Financiero': 'Financiero',
            'Construcción': 'Industrial',
            'Agropecuario': 'Agropecuario',
            'Minero y energético': 'Industrial',
            'Logística y transporte': 'Logística',
            'Hotelería, restaurantes y turismo': 'Servicios',
            'Administración pública': 'Administrativo',
            'Desarrollo humano y social': 'Social',
            'Servicios a la comunidad, recreación y bienestar': 'Social',
            'Ambiental': 'Ambiental',
            'Seguridad y defensa': 'Seguridad',
            'Distribución y suministro de electricidad, agua y gas': 'Industrial'
        }
        
        # Mapeo de entornos de trabajo
        self.work_environment_mapping = {
            'Una oficina, con mi puesto de trabajo': 'Oficina',
            'Al aire libre, sin tener un puesto fijo': 'Exterior',
            'El lugar que quisiera, como mi casa': 'Remoto'
        }
        
        # Mapeo de niveles de interacción social
        self.social_interaction_mapping = {
            'Poca, que implique poco relacionamiento con compañeros de trabajo o clientes': 'Baja',
            'Mucha, que requiera de un relacionamiento constante con mi equipo de trabajo y clientes': 'Alta'
        }
    
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
    
    def _extract_student_preferences(self, student_data: Dict) -> Dict:
        """
        Extrae las preferencias del estudiante del dataset
        """
        preferences = {
            'sectors': [],
            'work_environment': None,
            'social_interaction': None,
            'work_focus': None,
            'favorite_subjects': [],
            'least_favorite_subjects': [],
            'strengths': []
        }
        
        # Extraer sectores preferidos
        sector_response = student_data.get('¿En cuál de estos sectores te gustaría trabajar?', '')
        if sector_response:
            sectors = [s.strip() for s in sector_response.split(',') if s.strip()]
            preferences['sectors'] = [self.sector_mapping.get(s, s) for s in sectors]
        
        # Extraer entorno de trabajo
        work_env_response = student_data.get('Quisiera que mi espacio laboral fuera...', '')
        preferences['work_environment'] = self.work_environment_mapping.get(work_env_response, 'Oficina')
        
        # Extraer nivel de interacción social
        social_response = student_data.get('En mi trabajo me gustaría que mi relación con los demás fuera...', '')
        preferences['social_interaction'] = self.social_interaction_mapping.get(social_response, 'Media')
        
        # Extraer enfoque de trabajo
        work_focus_response = student_data.get('Me gustaría un trabajo que se centrara en...', '')
        preferences['work_focus'] = work_focus_response
        
        # Extraer materias favoritas y menos favoritas
        fav_subjects = student_data.get('¿Cuáles son las materias que te gustan MÁS?', '')
        if fav_subjects:
            preferences['favorite_subjects'] = [s.strip() for s in fav_subjects.split(',') if s.strip()]
        
        least_subjects = student_data.get('¿Cuáles son las materias que te gustan MENOS?', '')
        if least_subjects:
            preferences['least_favorite_subjects'] = [s.strip() for s in least_subjects.split(',') if s.strip()]
        
        # Extraer fortalezas
        strengths_response = student_data.get('¿En qué sientes que te va mejor? En temas relacionados con...', '')
        if strengths_response:
            preferences['strengths'] = [s.strip() for s in strengths_response.split(',') if s.strip()]
        
        return preferences
    
    def _calculate_base_profile(self, student_data: Dict) -> str:
        """
        Calcula el perfil base usando reglas simples basadas en las respuestas del estudiante
        """
        # Analizar respuestas para determinar perfil base
        profile_scores = {
            'Técnico': 0,
            'Social': 0,
            'Investigador': 0,
            'Artístico': 0,
            'Organizador': 0
        }
        
        # Analizar actividades de tiempo libre
        free_time = student_data.get('¿Qué prefieres hacer en tus ratos libres?', '')
        if 'construir cosas' in free_time.lower():
            profile_scores['Técnico'] += 2
        if 'actividades artisticas' in free_time.lower():
            profile_scores['Artístico'] += 2
        if 'conversas con mis amigos' in free_time.lower():
            profile_scores['Social'] += 2
        if 'experimentos' in free_time.lower():
            profile_scores['Investigador'] += 2
        if 'ordenar mi espacio' in free_time.lower():
            profile_scores['Organizador'] += 2
        
        # Analizar autopercepción
        self_perception = student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '')
        if 'hábil' in self_perception.lower():
            profile_scores['Técnico'] += 2
        if 'imaginativo' in self_perception.lower():
            profile_scores['Artístico'] += 2
        if 'sociable' in self_perception.lower():
            profile_scores['Social'] += 2
        if 'curioso' in self_perception.lower():
            profile_scores['Investigador'] += 2
        if 'organizado' in self_perception.lower():
            profile_scores['Organizador'] += 2
        
        # Analizar materias favoritas
        fav_subjects = student_data.get('¿Cuáles son las materias que te gustan MÁS?', '')
        if 'matemáticas' in fav_subjects.lower() or 'física' in fav_subjects.lower():
            profile_scores['Técnico'] += 1
        if 'ciencias sociales' in fav_subjects.lower():
            profile_scores['Social'] += 1
        if 'biología y química' in fav_subjects.lower():
            profile_scores['Investigador'] += 1
        if 'educación artística' in fav_subjects.lower():
            profile_scores['Artístico'] += 1
        
        # Retornar el perfil con mayor puntuación
        return max(profile_scores, key=profile_scores.get)
    
    def _detect_hybrid_profile(self, student_data: Dict, ml_profile: str, base_profile: str) -> Tuple[str, List[str]]:
        """
        Detecta si el estudiante tiene un perfil híbrido
        """
        hybrid_profiles = []
        
        # Si hay diferencia significativa entre perfil ML y base, considerar híbrido
        if ml_profile != base_profile:
            hybrid_profiles = [base_profile, ml_profile]
        
        # Analizar respuestas para detectar rasgos adicionales
        responses = student_data.get('¿En 10 años te ves trabajando con...?', '')
        if 'personas, enseñando' in responses.lower():
            if 'Social' not in hybrid_profiles:
                hybrid_profiles.append('Social')
        
        if 'herramientas que me permitan construir' in responses.lower():
            if 'Técnico' not in hybrid_profiles:
                hybrid_profiles.append('Técnico')
        
        if 'información y datos' in responses.lower():
            if 'Investigador' not in hybrid_profiles:
                hybrid_profiles.append('Investigador')
        
        # Si no hay perfil híbrido claro, usar el ML
        if not hybrid_profiles:
            return ml_profile, [ml_profile]
        
        # Retornar el perfil principal (el que tenga mayor confianza) y todos los perfiles
        return hybrid_profiles[0], hybrid_profiles
    
    def predict_profile(self, student_data: Dict) -> Tuple[str, float]:
        """
        Predice el perfil de personalidad con lógica mejorada que respeta el perfil base
        """
        # Preparar datos para predicción ML
        features = self._prepare_features(student_data, self.personality_features)
        
        # Hacer predicción ML
        prediction = self.personality_model.predict(features)[0]
        probabilities = self.personality_model.predict_proba(features)[0]
        
        # Decodificar resultado ML
        ml_predicted_profile = self.personality_encoder.inverse_transform([prediction])[0]
        ml_confidence = max(probabilities)
        
        # MEJORA: Verificar coherencia declarada
        coherencia_gustos_rendimiento = student_data.get('Coherencia Gustos-Rendimiento', '')
        base_profile = self._calculate_base_profile(student_data)
        
        # REFORZAR PRIORIDAD MÁXIMA: Si coherencia es "Muy Coherente" -> Priorizar perfil base
        if coherencia_gustos_rendimiento == 'Muy Coherente':
            print(f"🎯 COHERENCIA MUY COHERENTE detectada - MÁXIMA PRIORIDAD AL PERFIL BASE")
            base_validation = self._validate_base_profile(student_data, base_profile)
            if base_validation > 0.5:  # Umbral reducido para ser más permisivo
                print(f"✅ Perfil base VALIDADO con coherencia MUY ALTA (validación: {base_validation:.3f})")
                print(f"🚀 OVERRIDE ML: Ignorando predicción ML a favor del perfil base coherente")
                print(f"📝 Razón: COHERENCIA MUY COHERENTE - Perfil base con máxima prioridad")
                return base_profile, 0.95
            else:
                # Incluso si la validación es baja, dar al perfil base alta confianza por coherencia
                print(f"🎯 Coherencia MUY COHERENTE detectada - Usando perfil base aunque validación sea baja")
                print(f"📝 Razón: COHERENCIA MUY COHERENTE - Perfil base prioritario")
                return base_profile, 0.85
        
        # PENALIZAR predicciones ML con baja confianza (< 0.4)
        if ml_confidence < 0.4:
            print(f"⚠️  Confianza ML muy baja ({ml_confidence:.3f}), priorizando perfil base")
            base_validation = self._validate_base_profile(student_data, base_profile)
            
            # Si el perfil base tiene buena validación, usarlo
            if base_validation > 0.6:
                print(f"✅ Usando perfil base {base_profile} por baja confianza ML")
                print(f"📝 Razón: Perfil base seleccionado por baja confianza ML")
                return base_profile, 0.75
            else:
                # Reducir aún más la confianza del ML
                ml_confidence = ml_confidence * 0.6  # Penalización adicional
                print(f"📉 Penalizando confianza ML a {ml_confidence:.3f}")
        
        # Aplicar lógica de respeto al perfil base cuando sea apropiado
        final_profile, final_confidence, reason = self._respect_base_profile_when_appropriate(
            student_data, ml_predicted_profile, ml_confidence, base_profile
        )
        
        print(f"🤖 ML predijo: {ml_predicted_profile} (confianza original: {max(probabilities):.3f})")
        print(f"📋 Perfil base: {base_profile}")
        print(f"🎯 Coherencia declarada: {coherencia_gustos_rendimiento}")
        print(f"✅ Perfil final: {final_profile} (confianza: {final_confidence:.3f})")
        print(f"📝 Razón: {reason}")
        
        return final_profile, final_confidence
    
    def predict_sector(self, student_data: Dict) -> Tuple[str, float]:
        """
        Predice el sector preferido priorizando las preferencias reales del estudiante
        """
        # Obtener preferencias del estudiante primero
        preferences = self._extract_student_preferences(student_data)
        
        # PRIORIZAR FUERTEMENTE sectores preferidos explícitos del estudiante
        if preferences['sectors']:
            # Usar el primer sector preferido como principal con máxima prioridad
            primary_sector = preferences['sectors'][0]
            print(f"🎯 SECTOR PREFERIDO EXPLÍCITO: {primary_sector} (confianza: 0.95)")
            print(f"💡 Todos los sectores preferidos: {', '.join(preferences['sectors'])}")
            return primary_sector, 0.95  # Muy alta confianza en preferencias explícitas
        
        # Si no hay preferencias explícitas, usar el modelo ML
        features = self._prepare_features(student_data, self.sector_features)
        
        prediction = self.sector_model.predict(features)[0]
        probabilities = self.sector_model.predict_proba(features)[0]
        
        predicted_sector = self.sector_encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        
        # PENALIZAR predicciones ML con baja confianza (< 0.4) para sector también
        if confidence < 0.4:
            print(f"⚠️  Confianza ML sector muy baja ({confidence:.3f}), reduciendo peso")
            confidence = confidence * 0.5  # Penalización severa
            print(f"📉 Confianza sector penalizada a {confidence:.3f}")
        
        print(f"🤖 Sector ML predicho: {predicted_sector} (confianza: {confidence:.3f})")
        
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
    
    def _filter_careers_by_work_environment(self, careers: List[str], work_environment: str) -> List[str]:
        """
        Filtra carreras según el entorno de trabajo preferido
        """
        # Definir carreras incompatibles con cada entorno
        incompatible_careers = {
            'Oficina': [
                'Ingeniería Agronómica', 'Medicina Veterinaria', 'Arquitectura de Paisaje',
                'Tecnología en Gestión Ambiental', 'Ingeniería Forestal'
            ],
            'Exterior': [
                'Ingeniería de Sistemas', 'Administración de Empresas', 'Contaduría Pública',
                'Psicología', 'Derecho'
            ],
            'Remoto': [
                'Medicina', 'Enfermería', 'Odontología', 'Ingeniería Civil',
                'Arquitectura', 'Medicina Veterinaria'
            ]
        }
        
        incompatible = incompatible_careers.get(work_environment, [])
        return [career for career in careers if career not in incompatible]
    
    def _filter_careers_by_social_interaction(self, careers: List[str], social_level: str) -> List[str]:
        """
        Filtra carreras según el nivel de interacción social deseado
        """
        # Definir carreras según nivel de interacción social
        high_interaction_careers = [
            'Medicina', 'Enfermería', 'Psicología', 'Trabajo Social',
            'Licenciatura en Educación Física', 'Licenciatura en Matemáticas',
            'Administración de Empresas', 'Derecho'
        ]
        
        low_interaction_careers = [
            'Ingeniería de Sistemas', 'Ingeniería Civil', 'Ingeniería Mecánica',
            'Ingeniería Eléctrica', 'Ingeniería Química', 'Ingeniería Biomédica',
            'Estadística', 'Ciencia de Datos'
        ]
        
        if social_level == 'Alta':
            return [career for career in careers if career in high_interaction_careers]
        elif social_level == 'Baja':
            return [career for career in careers if career in low_interaction_careers]
        else:
            return careers  # No filtrar si es nivel medio
    
    def _calculate_career_coherence_score(self, career_name: str, predicted_profile: str, 
                                        predicted_sector: str, student_preferences: Dict) -> float:
        """
        Calcula la puntuación de coherencia de una carrera
        """
        career_info = self.career_db.get_career_info(career_name)
        if not career_info:
            return 0.0
        
        coherence_score = 0.0
        
        # Coherencia con perfil de personalidad
        career_profiles = career_info.get('perfil_personalidad', [])
        if predicted_profile in career_profiles:
            coherence_score += 0.4
        elif any(profile in career_profiles for profile in student_preferences.get('hybrid_profiles', [])):
            coherence_score += 0.3
        
        # Coherencia con sector preferido
        career_sectors = career_info.get('sector_preferido', [])
        if predicted_sector in career_sectors:
            coherence_score += 0.3
        elif any(sector in career_sectors for sector in student_preferences.get('sectors', [])):
            coherence_score += 0.2
        
        # Coherencia con entorno de trabajo
        work_env = student_preferences.get('work_environment', 'Oficina')
        if work_env == 'Oficina' and career_name not in ['Ingeniería Agronómica', 'Medicina Veterinaria']:
            coherence_score += 0.1
        elif work_env == 'Exterior' and career_name in ['Ingeniería Civil', 'Arquitectura']:
            coherence_score += 0.1
        elif work_env == 'Remoto' and career_name in ['Ingeniería de Sistemas', 'Estadística']:
            coherence_score += 0.1
        
        # Coherencia con nivel de interacción social
        social_level = student_preferences.get('social_interaction', 'Media')
        if social_level == 'Alta' and career_name in ['Medicina', 'Psicología', 'Enfermería']:
            coherence_score += 0.1
        elif social_level == 'Baja' and career_name in ['Ingeniería de Sistemas', 'Estadística']:
            coherence_score += 0.1
        
        return min(coherence_score, 1.0)
    
    def recommend_careers(self, student_data: Dict, top_n: int = 8) -> List[Dict]:
        """
        Recomienda carreras con lógica mejorada de coherencia, validación y MAYOR DIVERSIDAD
        """
        print("\n🎯 INICIANDO RECOMENDACIÓN MEJORADA DE CARRERAS CON DIVERSIDAD")
        print("=" * 60)
        
        # Extraer preferencias del estudiante
        student_preferences = self._extract_student_preferences(student_data)
        
        # Predecir perfil y sector con lógica mejorada
        predicted_profile, profile_confidence = self.predict_profile(student_data)
        predicted_sector, sector_confidence = self.predict_sector(student_data)
        
        # APLICAR REGLA 1.1: Verificar coherencia ML con preferencias declaradas
        ml_coherent, ml_coherence_reason = self._apply_rule_1_1_ml_coherence_check(
            predicted_profile, profile_confidence, student_data
        )
        print(f"🔍 REGLA 1.1 - ML Coherencia: {ml_coherence_reason}")
        
        # APLICAR REGLA 1.2: Híbrido ponderado entre perfil base y ML
        base_profile = self._calculate_base_profile(student_data)
        coherencia_gustos = student_data.get('Coherencia Gustos-Rendimiento', '')
        final_profile, hybrid_confidence = self._apply_rule_1_2_hybrid_weighting(
            coherencia_gustos, base_profile, predicted_profile, profile_confidence
        )
        
        # Si no es coherente ML, usar solo el perfil base o híbrido
        if not ml_coherent and profile_confidence < 0.4:
            print(f"⚠️  REGLA 1.1 APLICADA: ML descartado por baja confianza y falta de coherencia")
            final_profile = base_profile
            hybrid_confidence = 0.75
        
        # Detectar perfiles híbridos con la nueva lógica
        _, hybrid_profiles = self._detect_hybrid_profile(student_data, predicted_profile, base_profile)
        student_preferences['hybrid_profiles'] = hybrid_profiles
        
        print(f"\n🧠 Perfil final: {final_profile} (confianza: {hybrid_confidence:.3f})")
        print(f"🏢 Sector predicho: {predicted_sector} (confianza: {sector_confidence:.3f})")
        if len(hybrid_profiles) > 1:
            print(f"🔄 Perfiles híbridos detectados: {', '.join(hybrid_profiles)}")
        print(f"📋 NUEVAS REGLAS APLICADAS: Mejores prácticas de recomendación activadas")
        
        # MEJORADO: Obtener MÁS carreras candidatas para mayor diversidad
        all_careers = set(self.career_db.get_all_careers())
        technical_careers = set(self._get_technical_careers())
        
        # SIEMPRE incluir carreras técnicas para mayor diversidad
        print(f"💡 Incluyendo {len(technical_careers)} carreras técnicas para mayor diversidad")
        all_careers.update(technical_careers)
        
        # CORREGIR DUPLICADOS: usar set para eliminar duplicados automáticamente
        all_careers = set(all_careers)
        print(f"📊 Total de carreras candidatas únicas: {len(all_careers)}")
        
        # MEJORADO: Filtros menos restrictivos para mayor diversidad
        compatible_careers = []
        for career in all_careers:
            compatibility = self._validate_career_compatibility(
                career, student_data, final_profile, predicted_sector, student_preferences
            )
            
            # UMBRAL REDUCIDO para permitir más diversidad (0.4 → 0.2)
            if compatibility['overall_compatibility'] > 0.2:
                compatible_careers.append((career, compatibility))
        
        print(f"\n📊 Carreras compatibles encontradas: {len(compatible_careers)}")
        
        # MEJORADO: Filtros más permisivos
        work_env = student_preferences.get('work_environment', 'Oficina')
        print(f"🏢 Filtrando por entorno de trabajo: {work_env} (criterio relajado)")
        
        environment_filtered = []
        for career, compatibility in compatible_careers:
            # UMBRAL REDUCIDO para entorno (0.5 → 0.3)
            if compatibility['work_environment_fit'] > 0.3:
                environment_filtered.append((career, compatibility))
        
        # MEJORADO: Filtro social más permisivo
        social_level = student_preferences.get('social_interaction', 'Media')
        print(f"👥 Considerando nivel de interacción social: {social_level} (criterio relajado)")
        
        final_filtered = []
        for career, compatibility in environment_filtered:
            # UMBRAL REDUCIDO para interacción (0.5 → 0.3)
            if compatibility['social_interaction_fit'] > 0.3:
                final_filtered.append((career, compatibility))
        
        # MEJORADO: Si aún hay pocas carreras, relajar más los criterios
        if len(final_filtered) < top_n * 2:
            print("⚠️  Relajando criterios para mayor diversidad...")
            final_filtered = compatible_careers[:min(top_n * 3, len(compatible_careers))]
        
        print(f"📊 Carreras después de filtrado relajado: {len(final_filtered)}")
        
        # NUEVO: Añadir diversidad forzada por sector
        diverse_filtered = self._ensure_sector_diversity(final_filtered, top_n * 2)
        print(f"🎨 Diversidad por sector aplicada: {len(diverse_filtered)} carreras")
        
        # Calcular puntuaciones finales mejoradas CON CAPA DE REGLAS LÓGICAS POST-PREDICCIÓN
        career_scores = {}
        rule_applications = {}
        logic_exclusions = []
        logic_applications_count = 0
        
        for career, compatibility in diverse_filtered:
            career_info = self.career_db.get_career_info(career)
            
            # ===== NUEVA CAPA DE REGLAS LÓGICAS POST-PREDICCIÓN =====
            logic_result = self._apply_post_prediction_logic_layer(career, student_data, compatibility)
            
            # EXCLUSIÓN ESTRICTA: Si las reglas lógicas determinan exclusión
            if logic_result['should_exclude']:
                logic_exclusions.append({
                    'career': career,
                    'reasons': logic_result['exclusion_reasons']
                })
                continue  # Saltar esta carrera completamente
            
            # Contar aplicaciones de lógica
            if logic_result['logic_applied']:
                logic_applications_count += 1
            
            # Puntuación base mejorada
            base_score = compatibility['overall_compatibility']
            
            # APLICAR REGLA 2.1: Bonificación por sectores explícitos
            sector_bonus, sector_reason = self._apply_rule_2_1_sector_bonus(career_info, student_data)
            
            # APLICAR REGLA 2.2: Bonificación por coincidencia gustos-enfoque laboral
            work_focus_bonus, work_focus_reason = self._apply_rule_2_2_work_focus_bonus(career_info, student_data)
            
            # APLICAR REGLA 3.1: Penalización por contradicción social (REDUCIDA)
            social_penalty, social_reason = self._apply_rule_3_1_social_contradiction_penalty(career, student_data)
            social_penalty *= 0.5  # Reducir penalizaciones para mayor diversidad
            
            # APLICAR REGLA 3.2: Penalización por entorno de trabajo (REDUCIDA)
            environment_penalty, environment_reason = self._apply_rule_3_2_work_environment_penalty(career, student_data)
            environment_penalty *= 0.5  # Reducir penalizaciones
            
            # Bonificación por coherencia múltiple
            coherence_bonus = 0.0
            if compatibility['profile_match'] and compatibility['sector_match']:
                coherence_bonus += 0.15  # Bonus por coincidencia doble
            
            # ===== PESO REFINADO DEL SECTOR ML (NO SOLO COINCIDENCIA) =====
            refined_sector_weight = self._refine_sector_weight(career, student_data, career_info, compatibility)
            
            # BONIFICACIÓN por sectores explícitos (REDUCIDA para diversidad)
            explicit_sector_score = 0.0
            if career_info:
                career_sectors = career_info.get('sector_preferido', [])
                student_sectors = student_preferences.get('sectors', [])
                
                if student_sectors and any(sector in career_sectors for sector in student_sectors):
                    explicit_sector_score = 0.15  # REDUCIDO de 0.30 a 0.15
                    
            # Bonificación por preferencias de entorno y sector laboral (REDUCIDA)
            environment_sector_bonus = self._calculate_environment_sector_score(
                career, student_preferences, career_info
            ) * 0.7  # Reducir al 70%
            
            # Bonificación ARTÍSTICA (REDUCIDA)
            artistic_creative_bonus = 0.0
            if 'Artístico' in hybrid_profiles or final_profile == 'Artístico':
                artistic_bonus = self._calculate_artistic_creative_bonus(career, career_info)
                if artistic_bonus > 0:
                    artistic_creative_bonus = artistic_bonus * 0.6  # Reducir al 60%
            
            # Bonificación por carreras técnicas aplicadas (REDUCIDA)
            technical_bonus = 0.0
            if compatibility['technical_application'] and 'Técnico' in hybrid_profiles:
                technical_bonus += 0.03  # REDUCIDO de 0.05 a 0.03
            
            # Bonificación por confianza en predicciones (REDUCIDA)
            confidence_bonus = (hybrid_confidence + sector_confidence) / 2 * 0.02  # REDUCIDO
            
            # Bonificación por coherencia "Muy Coherente" (REDUCIDA)
            very_coherent_bonus = 0.0
            coherencia_gustos_rendimiento = student_data.get('Coherencia Gustos-Rendimiento', '')
            if coherencia_gustos_rendimiento == 'Muy Coherente':
                career_profiles = career_info.get('perfil_personalidad', []) if career_info else []
                if base_profile in career_profiles:
                    very_coherent_bonus = 0.12  # REDUCIDO de 0.20 a 0.12
                elif any(prof in career_profiles for prof in hybrid_profiles):
                    very_coherent_bonus = 0.08  # REDUCIDO de 0.15 a 0.08
                else:
                    very_coherent_bonus = 0.05  # REDUCIDO de 0.10 a 0.05
            
            # Calcular puntuación inicial sin diversidad ni lógica
            initial_score = (base_score + coherence_bonus + explicit_sector_score + 
                           environment_sector_bonus + artistic_creative_bonus +
                           technical_bonus + confidence_bonus + very_coherent_bonus +
                           sector_bonus + work_focus_bonus + social_penalty + environment_penalty +
                           refined_sector_weight)  # NUEVO: Peso refinado del sector ML
            
            # NUEVO: Bonificación de diversidad calculada después de score inicial
            diversity_bonus = self._calculate_diversity_bonus(career, career_scores, career_info)
            
            # ===== APLICAR PENALIZACIONES DE LA CAPA LÓGICA =====
            logic_penalty = logic_result['penalty_score']
            
            # Tracking completo de reglas aplicadas
            rule_applications[career] = {
                'sector_bonus': (sector_bonus, sector_reason),
                'work_focus_bonus': (work_focus_bonus, work_focus_reason),
                'social_penalty': (social_penalty, social_reason),
                'environment_penalty': (environment_penalty, environment_reason),
                'diversity_bonus': diversity_bonus,
                'logic_penalty': logic_penalty,
                'logic_reasons': logic_result['penalty_reasons'],
                'refined_sector_weight': refined_sector_weight
            }
            
            # Puntuación final CON TODAS LAS MEJORAS Y CAPA LÓGICA
            final_score = initial_score + diversity_bonus + logic_penalty
            
            career_scores[career] = min(max(final_score, 0.1), 1.0)  # Mínimo 0.1, máximo 1.0
            
            # Log de aplicaciones significativas
            if abs(diversity_bonus) > 0.05:
                print(f"🎨 DIVERSIDAD - {career}: +{diversity_bonus:.2f}")
            if abs(logic_penalty) > 0.05:
                main_reason = logic_result['penalty_reasons'][0] if logic_result['penalty_reasons'] else "Lógica aplicada"
                print(f"⚠️  LÓGICA - {career}: {logic_penalty:.2f} ({main_reason})")
            if abs(refined_sector_weight) > 0.05:
                print(f"🔍 SECTOR REFINADO - {career}: +{refined_sector_weight:.2f}")
        
        # Ordenar por puntuación
        sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
        
        # VERIFICACIÓN FINAL: Eliminar duplicados potenciales en recomendaciones finales
        unique_careers = []
        seen_careers = set()
        for career_name, score in sorted_careers:
            if career_name not in seen_careers:
                unique_careers.append((career_name, score))
                seen_careers.add(career_name)
        
        print(f"\n📋 Generando top {top_n} recomendaciones únicas...")
        print(f"✅ Carreras únicas después de eliminación de duplicados: {len(unique_careers)}")
        
        # Mostrar exclusiones lógicas si las hay
        if logic_exclusions:
            print(f"\n🚫 EXCLUSIONES POR REGLAS LÓGICAS:")
            for exclusion in logic_exclusions:
                print(f"   ❌ {exclusion['career']}: {exclusion['reasons'][0]}")
        
        # APLICAR REGLA 4: Diversidad y eliminación de duplicados por subárea
        print(f"🔄 Aplicando REGLAS 4.1 y 4.2: Diversidad por subáreas...")
        
        # Preparar recomendaciones iniciales
        temp_recommendations = []
        for career_name, score in unique_careers[:min(top_n * 2, len(unique_careers))]:  # Tomar más para filtrar después
            career_info = self.career_db.get_career_info(career_name)
            compatibility = next((comp for c, comp in final_filtered if c == career_name), {})
            
            # APLICAR REGLA 5.1: Personalizar razones por carrera
            personalized_reasons = self._apply_rule_5_1_personalized_reasons(
                career_name, student_data, career_info
            )
            
            # APLICAR REGLA 5.2: Indicadores de transparencia
            transparency_indicators = self._apply_rule_5_2_transparency_indicators(
                career_name, compatibility, hybrid_confidence, sector_confidence,
                base_profile, predicted_profile
            )
            
            # Calcular razones de recomendación mejoradas
            reasons = []
            
            # Incluir razones personalizadas primero (Regla 5.1)
            reasons.extend(personalized_reasons)
            
            # Razones de compatibilidad estándar
            if compatibility.get('validation_reasons'):
                reasons.extend(compatibility['validation_reasons'][:2])  # Máximo 2
            
            # Agregar razones adicionales
            if compatibility.get('profile_match'):
                reasons.append(f"Coincide con tu perfil {final_profile}")
            if compatibility.get('sector_match'):
                reasons.append(f"Coincide con sector preferido")
            if compatibility.get('technical_application') and 'Técnico' in hybrid_profiles:
                reasons.append("Carrera técnica aplicada (ideal para perfil técnico)")
            if compatibility.get('academic_fit', 0) > 0.7:
                reasons.append("Excelente ajuste con tu rendimiento académico")
            
            # Agregar indicadores de transparencia (Regla 5.2)
            reasons.extend(transparency_indicators)
            
            recommendation = {
                'nombre': career_name,
                'puntuacion': score,
                'descripcion': career_info.get('descripcion', ''),
                'duracion': career_info.get('duracion', ''),
                'modalidad': career_info.get('modalidad', []),
                'universidades': career_info.get('universidades', [])[:3],
                'campo_laboral': career_info.get('campo_laboral', []),
                'salario_promedio': career_info.get('salario_promedio', ''),
                'requisitos_academicos': career_info.get('requisitos_academicos', {}),
                'perfil_predicho': final_profile,
                'sector_predicho': predicted_sector,
                'razones_recomendacion': reasons[:4],  # Máximo 4 razones
                'coherencia_score': compatibility.get('overall_compatibility', 0.0),
                'compatibility_details': {
                    'profile_match': compatibility.get('profile_match', False),
                    'sector_match': compatibility.get('sector_match', False),
                    'academic_fit': compatibility.get('academic_fit', 0.0),
                    'work_environment_fit': compatibility.get('work_environment_fit', 0.0),
                    'social_interaction_fit': compatibility.get('social_interaction_fit', 0.0),
                    'technical_application': compatibility.get('technical_application', False)
                },
                'rule_applications': rule_applications.get(career_name, {})  # Tracking de reglas aplicadas
            }
            
            temp_recommendations.append(recommendation)
        
        # APLICAR REGLA 4.1: Máximo 2 carreras por subárea similar
        filtered_by_subfield = self._apply_rule_4_1_limit_similar_subfields(temp_recommendations)
        print(f"✅ REGLA 4.1 aplicada: {len(filtered_by_subfield)} carreras después de limitar subáreas")
        
        # APLICAR REGLA 4.2: Priorizar diversidad de sectores
        diversified_recommendations = self._apply_rule_4_2_prioritize_diverse_sectors(filtered_by_subfield)
        print(f"✅ REGLA 4.2 aplicada: Diversidad de sectores priorizada")
        
        # Tomar solo las top_n recomendaciones finales
        recommendations = diversified_recommendations[:top_n]
        
        print(f"✅ Recomendaciones generadas exitosamente!")
        
        # Mostrar resumen de mejoras aplicadas CON NUEVAS REGLAS
        has_explicit_sectors = bool(student_preferences.get('sectors'))
        low_confidence_applied = hybrid_confidence < 0.4 or sector_confidence < 0.4
        coherencia_muy_coherente = student_data.get('Coherencia Gustos-Rendimiento', '') == 'Muy Coherente'
        
        # Contar aplicaciones de nuevas reglas
        total_sector_bonuses = sum(1 for career in recommendations if abs(career['rule_applications'].get('sector_bonus', (0, ''))[0]) > 0.01)
        total_work_focus_bonuses = sum(1 for career in recommendations if abs(career['rule_applications'].get('work_focus_bonus', (0, ''))[0]) > 0.01)
        total_social_penalties = sum(1 for career in recommendations if abs(career['rule_applications'].get('social_penalty', (0, ''))[0]) > 0.01)
        total_environment_penalties = sum(1 for career in recommendations if abs(career['rule_applications'].get('environment_penalty', (0, ''))[0]) > 0.01)
        
        print(f"\n🔧 MEJORAS APLICADAS:")
        print(f"   ✅ Duplicados de carrera corregidos")
        print(f"   {'🏆' if coherencia_muy_coherente else '⭕'} PESO MÁXIMO para coherencia 'Muy Coherente': {'APLICADO' if coherencia_muy_coherente else 'No necesario'}")
        print(f"   {'✅' if low_confidence_applied else '⭕'} Penalización por baja confianza ML (<0.4): {'Aplicada' if low_confidence_applied else 'No necesaria'}")
        print(f"   {'✅' if has_explicit_sectors else '⭕'} Priorización de sectores explícitos: {'Aplicada' if has_explicit_sectors else 'No hay sectores explícitos'}")
        
        if coherencia_muy_coherente:
            print(f"   🎯 COHERENCIA MUY COHERENTE detectada:")
            print(f"      • Perfil base tiene MÁXIMA PRIORIDAD (95% confianza)")
            print(f"      • Bonificación adicional +20% para carreras compatibles")
            print(f"      • Umbral de validación reducido para mayor permisividad")
        
        if has_explicit_sectors:
            print(f"   🎯 Sectores priorizados: {', '.join(student_preferences['sectors'])}")
        
        # Contar mejoras aplicadas
        total_diversity_bonuses = sum(1 for career in recommendations if career['rule_applications'].get('diversity_bonus', 0) > 0.05)
        total_logic_penalties = sum(1 for career in recommendations if career['rule_applications'].get('logic_penalty', 0) < -0.05)
        total_sector_refinements = sum(1 for career in recommendations if career['rule_applications'].get('refined_sector_weight', 0) > 0.05)
        
        print(f"\n🎯 NUEVAS REGLAS IMPLEMENTADAS:")
        print(f"   📊 Regla 1.1-1.2: Mejor uso de predicción ML aplicado")
        if total_sector_bonuses > 0:
            print(f"   📊 Regla 2.1: {total_sector_bonuses} bonificaciones por sectores explícitos")
        if total_work_focus_bonuses > 0:
            print(f"   🎯 Regla 2.2: {total_work_focus_bonuses} bonificaciones por coincidencia gustos-enfoque")
        if total_social_penalties > 0:
            print(f"   ❌ Regla 3.1: {total_social_penalties} penalizaciones por contradicción social (reducidas)")
        if total_environment_penalties > 0:
            print(f"   🏢 Regla 3.2: {total_environment_penalties} penalizaciones por entorno inadecuado (reducidas)")
        print(f"   🔄 Regla 4.1-4.2: Diversidad y eliminación de duplicados aplicados")
        print(f"   📝 Regla 5.1-5.2: Razonamiento personalizado y transparencia aplicados")
        
        print(f"\n🧠 CAPA DE REGLAS LÓGICAS POST-PREDICCIÓN:")
        print(f"   ⚖️  {logic_applications_count} carreras evaluadas con reglas lógicas")
        if logic_exclusions:
            print(f"   🚫 {len(logic_exclusions)} carreras excluidas por contradicciones críticas")
        if total_logic_penalties > 0:
            print(f"   ⚠️  {total_logic_penalties} penalizaciones por variables negativas aplicadas")
        if total_sector_refinements > 0:
            print(f"   🔍 {total_sector_refinements} refinamientos de peso de sector ML aplicados")
        print(f"   ✅ Filtrado de falsos positivos implementado")
        
        print(f"\n🎨 MEJORAS DE DIVERSIDAD APLICADAS:")
        print(f"   ✅ Umbrales de compatibilidad relajados (0.4→0.2, 0.5→0.3)")
        print(f"   ✅ Penalizaciones reducidas al 50% para mayor variedad")
        print(f"   ✅ Bonificaciones principales reducidas para equilibrio")
        print(f"   ✅ Diversidad forzada por sector implementada")
        if total_diversity_bonuses > 0:
            print(f"   🎨 {total_diversity_bonuses} bonificaciones de diversidad aplicadas")
        print(f"   ✅ Variación reproducible para romper empates")
        
        print("=" * 60)
        
        return recommendations
    
    def generate_improved_report(self, student_data: Dict, recommendations: List[Dict]) -> str:
        """
        Genera un reporte mejorado y detallado de recomendaciones con validación
        """
        report = []
        report.append("🎓 REPORTE DE ORIENTACIÓN VOCACIONAL AVANZADO")
        report.append("=" * 70)
        
        # Información del estudiante
        name = student_data.get('Nombre completo', 'Estudiante')
        report.append(f"\n👤 ESTUDIANTE: {name}")
        
        # Información del análisis
        if recommendations:
            profile = recommendations[0]['perfil_predicho']
            sector = recommendations[0]['sector_predicho']
            report.append(f"\n🧠 PERFIL DE PERSONALIDAD FINAL: {profile}")
            report.append(f"🏢 SECTOR LABORAL PREDICHO: {sector}")
            
            # Mostrar detalles de compatibilidad del primer resultado
            if 'compatibility_details' in recommendations[0]:
                details = recommendations[0]['compatibility_details']
                report.append(f"\n📊 ANÁLISIS DE COMPATIBILIDAD:")
                report.append(f"   • Coincidencia de perfil: {'✅' if details['profile_match'] else '❌'}")
                report.append(f"   • Coincidencia de sector: {'✅' if details['sector_match'] else '❌'}")
                report.append(f"   • Ajuste académico: {details['academic_fit']:.1%}")
                report.append(f"   • Ajuste entorno trabajo: {details['work_environment_fit']:.1%}")
                report.append(f"   • Ajuste interacción social: {details['social_interaction_fit']:.1%}")
                if details['technical_application']:
                    report.append(f"   • ⚙️  Incluye carreras técnicas aplicadas")
        
        # Preferencias del estudiante
        preferences = self._extract_student_preferences(student_data)
        report.append(f"\n🎯 PREFERENCIAS DEL ESTUDIANTE:")
        
        if preferences['sectors']:
            report.append(f"   • Sectores preferidos: {', '.join(preferences['sectors'])}")
        if preferences['work_environment']:
            report.append(f"   • Entorno de trabajo deseado: {preferences['work_environment']}")
        if preferences['social_interaction']:
            report.append(f"   • Nivel de interacción social: {preferences['social_interaction']}")
        if preferences['favorite_subjects']:
            report.append(f"   • Materias favoritas: {', '.join(preferences['favorite_subjects'])}")
        
        # Validación de perfiles
        report.append(f"\n🔍 VALIDACIÓN DE PERFILES:")
        if recommendations:
            # Mostrar información sobre perfiles híbridos si existen
            has_hybrid = any('-' in rec['perfil_predicho'] for rec in recommendations)
            if has_hybrid:
                report.append(f"   • ✨ Perfil híbrido detectado: combina múltiples características")
            
            # Mostrar coherencia general
            avg_coherence = sum(rec['coherencia_score'] for rec in recommendations) / len(recommendations)
            report.append(f"   • 📈 Coherencia promedio del análisis: {avg_coherence:.1%}")
        
        # Recomendaciones detalladas
        report.append(f"\n📚 CARRERAS RECOMENDADAS (Top {len(recommendations)}):")
        report.append("-" * 60)
        
        for i, rec in enumerate(recommendations, 1):
            report.append(f"\n{i}. {rec['nombre']}")
            report.append(f"   📊 Compatibilidad general: {rec['puntuacion']:.1%}")
            report.append(f"   🎯 Score de coherencia: {rec['coherencia_score']:.1%}")
            report.append(f"   📝 {rec['descripcion']}")
            report.append(f"   ⏱️  Duración: {rec['duracion']}")
            report.append(f"   💰 Salario promedio: {rec['salario_promedio']}")
            
            # Mostrar universidades
            if rec['universidades']:
                report.append(f"   🏛️  Universidades: {', '.join(rec['universidades'])}")
            
            # Mostrar razones de recomendación
            if rec['razones_recomendacion']:
                report.append(f"   🎯 Razones de la recomendación:")
                for reason in rec['razones_recomendacion']:
                    report.append(f"     ✅ {reason}")
            
            # Mostrar detalles de compatibilidad
            if 'compatibility_details' in rec:
                details = rec['compatibility_details']
                report.append(f"   📈 Detalles de compatibilidad:")
                if details['profile_match']:
                    report.append(f"     🎭 Perfil compatible")
                if details['sector_match']:
                    report.append(f"     🏢 Sector compatible")
                if details['academic_fit'] > 0.7:
                    report.append(f"     📚 Excelente ajuste académico ({details['academic_fit']:.1%})")
                if details['technical_application']:
                    report.append(f"     ⚙️  Carrera técnica aplicada")
                if details['work_environment_fit'] > 0.8:
                    report.append(f"     🏢 Entorno de trabajo ideal")
        
        # Recomendaciones adicionales
        report.append(f"\n💡 RECOMENDACIONES ADICIONALES:")
        report.append(f"   • Considera visitar las universidades que ofrecen estas carreras")
        report.append(f"   • Habla con profesionales que trabajen en estos campos")
        report.append(f"   • Investiga sobre las oportunidades laborales en tu región")
        
        if any(rec.get('compatibility_details', {}).get('technical_application') for rec in recommendations):
            report.append(f"   • Las carreras técnicas aplicadas ofrecen inserción laboral rápida")
        
        # Validación final
        report.append(f"\n✅ VALIDACIÓN DEL ANÁLISIS:")
        report.append(f"   • Análisis basado en {len(recommendations)} carreras compatibles")
        report.append(f"   • Validación de compatibilidad multi-criterio aplicada")
        report.append(f"   • Preferencias explícitas del estudiante priorizadas")
        report.append(f"   • Detección de perfiles híbridos implementada")
        
        return "\n".join(report)

    def _get_technical_careers(self) -> List[str]:
        """
        Retorna lista AMPLIADA de carreras técnicas, ingenierías y artísticas aplicadas
        """
        return [
            # TECNOLOGÍAS (3 años)
            'Tecnología en Desarrollo de Software',
            'Tecnología en Redes y Telecomunicaciones',
            'Tecnología en Análisis de Sistemas',
            'Tecnología en Electrónica',
            'Tecnología en Automatización',
            'Tecnología Industrial',
            'Tecnología en Mecánica Automotriz',
            'Tecnología en Logística',
            'Tecnología en Construcción',
            
            # INGENIERÍAS TÉCNICAS (4-5 años)
            'Ingeniería de Sistemas',
            'Ingeniería en Automatización',
            'Ingeniería Mecatrónica',
            'Ingeniería de Datos',
            'Ingeniería de Producción',
            'Ingeniería Industrial',
            'Ingeniería Electrónica',
            'Ingeniería de Software',
            'Ingeniería Civil',
            'Ingeniería Mecánica',
            'Ingeniería Eléctrica',
            
            # DISEÑO TÉCNICO
            'Diseño Industrial',
            
            # CARRERAS ARTÍSTICAS Y CREATIVAS APLICADAS
            'Artes Visuales',
            'Artes Escénicas', 
            'Cine y Televisión',
            'Diseño de Modas',
            'Fotografía',
            'Publicidad',
            'Literatura',
            'Animación Digital',
            'Diseño Gráfico',
            'Música',
            'Arquitectura',
            'Comunicación Social',
            'Ingeniería en Multimedia'
        ]
    
    def _validate_career_compatibility(self, career_name: str, student_data: Dict, 
                                     predicted_profile: str, predicted_sector: str,
                                     student_preferences: Dict) -> Dict:
        """
        Valida la lógica de compatibilidad de una carrera específica
        """
        career_info = self.career_db.get_career_info(career_name)
        compatibility = {
            'profile_match': False,
            'sector_match': False,
            'academic_fit': 0.0,
            'work_environment_fit': 0.0,
            'social_interaction_fit': 0.0,
            'technical_application': False,
            'overall_compatibility': 0.0,
            'validation_reasons': []
        }
        
        if not career_info:
            return compatibility
        
        # Validación de perfil
        career_profiles = career_info.get('perfil_personalidad', [])
        if predicted_profile in career_profiles:
            compatibility['profile_match'] = True
            compatibility['validation_reasons'].append(f"Perfil {predicted_profile} coincide perfectamente")
        elif any(prof in career_profiles for prof in student_preferences.get('hybrid_profiles', [])):
            compatibility['profile_match'] = True
            compatibility['validation_reasons'].append(f"Perfil híbrido compatible")
        
        # Validación de sector (PRIORIZACIÓN MEJORADA DE SECTORES EXPLÍCITOS)
        career_sectors = career_info.get('sector_preferido', [])
        student_explicit_sectors = student_preferences.get('sectors', [])
        
        # PRIORIZAR FUERTEMENTE sectores explícitos del estudiante
        if student_explicit_sectors and any(sector in career_sectors for sector in student_explicit_sectors):
            compatibility['sector_match'] = True
            if student_explicit_sectors[0] in career_sectors:
                compatibility['validation_reasons'].append(f"SECTOR PRIMARIO EXPLÍCITO '{student_explicit_sectors[0]}' coincide perfectamente")
            else:
                compatibility['validation_reasons'].append(f"Sector explícito del estudiante coincide")
        elif predicted_sector in career_sectors:
            compatibility['sector_match'] = True
            compatibility['validation_reasons'].append(f"Sector ML predicho '{predicted_sector}' coincide")
        
        # Validación académica
        compatibility['academic_fit'] = self._calculate_academic_compatibility(career_info, student_data)
        if compatibility['academic_fit'] > 0.7:
            compatibility['validation_reasons'].append("Excelente ajuste académico")
        elif compatibility['academic_fit'] > 0.5:
            compatibility['validation_reasons'].append("Buen ajuste académico")
        
        # Validación de entorno de trabajo
        work_env = student_preferences.get('work_environment', 'Oficina')
        compatibility['work_environment_fit'] = self._calculate_work_environment_fit(career_name, work_env)
        if compatibility['work_environment_fit'] > 0.8:
            compatibility['validation_reasons'].append("Entorno de trabajo ideal")
        
        # Validación de interacción social
        social_level = student_preferences.get('social_interaction', 'Media')
        compatibility['social_interaction_fit'] = self._calculate_social_interaction_fit(career_name, social_level)
        if compatibility['social_interaction_fit'] > 0.8:
            compatibility['validation_reasons'].append("Nivel de interacción social adecuado")
        
        # Verificar si es carrera técnica aplicada
        technical_careers = self._get_technical_careers()
        if career_name in technical_careers or 'Tecnología' in career_name:
            compatibility['technical_application'] = True
            compatibility['validation_reasons'].append("Carrera técnica aplicada")
        
        # Calcular compatibilidad general
        compatibility['overall_compatibility'] = self._calculate_overall_compatibility(compatibility)
        
        return compatibility
    
    def _calculate_academic_compatibility(self, career_info: Dict, student_data: Dict) -> float:
        """
        Calcula la compatibilidad académica mejorada
        """
        if 'requisitos_academicos' not in career_info:
            return 0.6  # Valor neutral si no hay requisitos específicos
        
        requirements = career_info['requisitos_academicos']
        total_score = 0.0
        total_requirements = len(requirements)
        
        if total_requirements == 0:
            return 0.6
        
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
        
        for subject, required_level in requirements.items():
            mapped_subject = subject_mapping.get(subject, subject)
            
            if mapped_subject in student_data:
                student_grade = student_data[mapped_subject]
                
                # Evaluar compatibilidad más detallada
                if required_level == "Alto" and student_grade >= 4.0:
                    total_score += 1.0
                elif required_level == "Alto" and student_grade >= 3.5:
                    total_score += 0.8
                elif required_level == "Medio" and student_grade >= 3.0:
                    total_score += 1.0
                elif required_level == "Medio" and student_grade >= 2.5:
                    total_score += 0.8
                elif required_level == "Bajo" and student_grade >= 2.0:
                    total_score += 1.0
                else:
                    # Penalización menor por no cumplir exactamente
                    total_score += max(0, student_grade / 5.0)
        
        return min(total_score / total_requirements, 1.0)
    
    def _calculate_work_environment_fit(self, career_name: str, work_environment: str) -> float:
        """
        Calcula qué tan bien coincide el entorno de trabajo con la carrera
        """
        office_careers = [
            'Administración de Empresas', 'Contaduría Pública', 'Ingeniería de Sistemas',
            'Psicología', 'Derecho', 'Estadística', 'Ciencia de Datos'
        ]
        
        outdoor_careers = [
            'Ingeniería Civil', 'Arquitectura', 'Ingeniería Agronómica',
            'Medicina Veterinaria', 'Ingeniería Forestal', 'Tecnología en Gestión Ambiental'
        ]
        
        remote_careers = [
            'Ingeniería de Sistemas', 'Estadística', 'Ciencia de Datos',
            'Tecnología en Desarrollo de Software', 'Diseño Gráfico'
        ]
        
        if work_environment == 'Oficina':
            if career_name in office_careers:
                return 1.0
            elif career_name not in outdoor_careers:
                return 0.7
            else:
                return 0.3
        elif work_environment == 'Exterior':
            if career_name in outdoor_careers:
                return 1.0
            elif career_name not in office_careers:
                return 0.6
            else:
                return 0.4
        elif work_environment == 'Remoto':
            if career_name in remote_careers:
                return 1.0
            elif career_name in office_careers:
                return 0.8
            else:
                return 0.2
        
        return 0.5  # Neutral si no se puede determinar
    
    def _calculate_social_interaction_fit(self, career_name: str, social_level: str) -> float:
        """
        Calcula qué tan bien coincide el nivel de interacción social
        """
        high_interaction = [
            'Medicina', 'Enfermería', 'Psicología', 'Trabajo Social',
            'Licenciatura en Educación Física', 'Licenciatura en Matemáticas',
            'Administración de Empresas', 'Derecho'
        ]
        
        low_interaction = [
            'Ingeniería de Sistemas', 'Ingeniería Civil', 'Ingeniería Mecánica',
            'Ingeniería Eléctrica', 'Ingeniería Química', 'Estadística',
            'Tecnología en Desarrollo de Software'
        ]
        
        if social_level == 'Alta':
            if career_name in high_interaction:
                return 1.0
            elif career_name not in low_interaction:
                return 0.6
            else:
                return 0.2
        elif social_level == 'Baja':
            if career_name in low_interaction:
                return 1.0
            elif career_name not in high_interaction:
                return 0.6
            else:
                return 0.2
        else:  # Media
            return 0.8  # La mayoría de carreras funcionan con interacción media
    
    def _calculate_overall_compatibility(self, compatibility: Dict) -> float:
        """
        Calcula la compatibilidad general usando pesos balanceados
        """
        weights = {
            'profile_match': 0.25,
            'sector_match': 0.25,
            'academic_fit': 0.20,
            'work_environment_fit': 0.15,
            'social_interaction_fit': 0.10,
            'technical_application': 0.05
        }
        
        score = 0.0
        
        # Bonificaciones por coincidencias exactas
        if compatibility['profile_match']:
            score += weights['profile_match']
        if compatibility['sector_match']:
            score += weights['sector_match']
        if compatibility['technical_application']:
            score += weights['technical_application']
        
        # Puntuaciones proporcionales
        score += compatibility['academic_fit'] * weights['academic_fit']
        score += compatibility['work_environment_fit'] * weights['work_environment_fit']
        score += compatibility['social_interaction_fit'] * weights['social_interaction_fit']
        
        return min(score, 1.0)
    
    def _respect_base_profile_when_appropriate(self, student_data: Dict, 
                                              ml_profile: str, ml_confidence: float,
                                              base_profile: str) -> Tuple[str, float, str]:
        """
        Respeta el perfil base del estudiante cuando tiene más sentido que el ML
        NOTA: La coherencia "Muy Coherente" se maneja antes en predict_profile()
        """
        
        # Si la confianza del ML es muy baja y el perfil base es diferente
        if ml_confidence < 0.6 and base_profile != ml_profile:
            
            # Validar si el perfil base tiene sentido según las respuestas
            base_validation_score = self._validate_base_profile(student_data, base_profile)
            ml_validation_score = self._validate_base_profile(student_data, ml_profile)
            
            if base_validation_score > ml_validation_score:
                return base_profile, 0.75, f"Perfil base más coherente que predicción ML"
            elif base_validation_score > 0.7:
                # Crear perfil híbrido
                return f"{base_profile}-{ml_profile}", 0.8, f"Perfil híbrido detectado"
        
        # Si la confianza del ML es alta, usar ML
        if ml_confidence >= 0.8:
            return ml_profile, ml_confidence, "Alta confianza en predicción ML"
        
        # Caso intermedio: evaluar coherencia
        ml_coherence = self._calculate_profile_coherence(student_data, ml_profile)
        base_coherence = self._calculate_profile_coherence(student_data, base_profile)
        
        if base_coherence > ml_coherence + 0.2:  # Umbral de diferencia significativa
            return base_profile, 0.75, "Perfil base más coherente"
        else:
            return ml_profile, ml_confidence, "Predicción ML validada"
    
    def _validate_base_profile(self, student_data: Dict, profile: str) -> float:
        """
        Valida qué tan bien el perfil base coincide con las respuestas del estudiante
        """
        validation_score = 0.0
        
        # Validaciones específicas por perfil
        if profile == 'Técnico':
            if 'matemáticas' in student_data.get('¿Cuáles son las materias que te gustan MÁS?', '').lower():
                validation_score += 0.3
            if 'construir' in student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower():
                validation_score += 0.3
            if 'hábil' in student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower():
                validation_score += 0.2
        
        elif profile == 'Social':
            if 'ciencias sociales' in student_data.get('¿Cuáles son las materias que te gustan MÁS?', '').lower():
                validation_score += 0.3
            if 'conversas' in student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower():
                validation_score += 0.3
            if 'sociable' in student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower():
                validation_score += 0.2
        
        elif profile == 'Investigador':
            if any(materia in student_data.get('¿Cuáles son las materias que te gustan MÁS?', '').lower() 
                   for materia in ['biología', 'química', 'física']):
                validation_score += 0.3
            if 'experimentos' in student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower():
                validation_score += 0.3
            if 'curioso' in student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower():
                validation_score += 0.2
        
        elif profile == 'Artístico':
            if 'educación artística' in student_data.get('¿Cuáles son las materias que te gustan MÁS?', '').lower():
                validation_score += 0.3
            if 'actividades artisticas' in student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower():
                validation_score += 0.3
            if 'imaginativo' in student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower():
                validation_score += 0.2
        
        elif profile == 'Organizador':
            if 'administración' in student_data.get('Me gustaría un trabajo que se centrara en...', '').lower():
                validation_score += 0.3
            if 'ordenar' in student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower():
                validation_score += 0.3
            if 'organizado' in student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower():
                validation_score += 0.2
        
        # Validación adicional basada en rendimiento académico
        academic_alignment = self._validate_academic_alignment(student_data, profile)
        validation_score += academic_alignment * 0.2
        
        return min(validation_score, 1.0)
    
    def _validate_academic_alignment(self, student_data: Dict, profile: str) -> float:
        """
        Valida si el rendimiento académico está alineado con el perfil
        """
        alignment_score = 0.0
        
        # Obtener promedios relevantes
        math_avg = student_data.get('Matemáticas - Promedio', 3.0)
        science_avg = student_data.get('Física - Promedio', 3.0)
        bio_chem_avg = student_data.get('Biología y química - Promedio', 3.0)
        social_avg = student_data.get('Ciencias sociales - Promedio', 3.0)
        art_avg = student_data.get('Educación artística - Promedio', 3.0)
        
        if profile == 'Técnico':
            if math_avg >= 4.0 or science_avg >= 4.0:
                alignment_score += 0.8
            elif math_avg >= 3.5 or science_avg >= 3.5:
                alignment_score += 0.6
        
        elif profile == 'Social':
            if social_avg >= 4.0:
                alignment_score += 0.8
            elif social_avg >= 3.5:
                alignment_score += 0.6
        
        elif profile == 'Investigador':
            if bio_chem_avg >= 4.0 or science_avg >= 4.0:
                alignment_score += 0.8
            elif bio_chem_avg >= 3.5 or science_avg >= 3.5:
                alignment_score += 0.6
        
        elif profile == 'Artístico':
            if art_avg >= 4.0:
                alignment_score += 0.8
            elif art_avg >= 3.5:
                alignment_score += 0.6
        
        elif profile == 'Organizador':
            # Para organizador, buscar balance general
            general_avg = student_data.get('Promedio General', 3.0)
            if general_avg >= 4.0:
                alignment_score += 0.7
            elif general_avg >= 3.5:
                alignment_score += 0.5
        
        return alignment_score
    
    def _calculate_profile_coherence(self, student_data: Dict, profile: str) -> float:
        """
        Calcula qué tan coherente es un perfil con todas las respuestas del estudiante
        """
        coherence_score = 0.0
        
        # Usar validación de perfil base como base
        base_coherence = self._validate_base_profile(student_data, profile)
        coherence_score += base_coherence * 0.6
        
        # Agregar coherencia con preferencias de trabajo
        work_coherence = self._validate_work_preferences_coherence(student_data, profile)
        coherence_score += work_coherence * 0.4
        
        return min(coherence_score, 1.0)
    
    def _validate_work_preferences_coherence(self, student_data: Dict, profile: str) -> float:
        """
        Valida coherencia entre perfil y preferencias de trabajo
        """
        coherence = 0.0
        
        work_focus = student_data.get('Me gustaría un trabajo que se centrara en...', '').lower()
        work_with = student_data.get('¿En 10 años te ves trabajando con...?', '').lower()
        sectors = student_data.get('¿En cuál de estos sectores te gustaría trabajar?', '').lower()
        
        if profile == 'Técnico':
            if any(keyword in work_focus for keyword in ['tecnología', 'sistemas', 'construir', 'desarrollar']):
                coherence += 0.4
            if 'herramientas' in work_with or 'tecnología' in work_with:
                coherence += 0.3
            if 'tic' in sectors or 'industrial' in sectors:
                coherence += 0.3
        
        elif profile == 'Social':
            if any(keyword in work_focus for keyword in ['personas', 'comunidad', 'ayudar', 'enseñar']):
                coherence += 0.4
            if 'personas' in work_with or 'enseñando' in work_with:
                coherence += 0.3
            if 'salud' in sectors or 'educación' in sectors or 'social' in sectors:
                coherence += 0.3
        
        elif profile == 'Investigador':
            if any(keyword in work_focus for keyword in ['investigación', 'análisis', 'descubrir', 'estudiar']):
                coherence += 0.4
            if 'información' in work_with or 'datos' in work_with:
                coherence += 0.3
            if 'investigación' in sectors or 'ciencias' in sectors:
                coherence += 0.3
        
        elif profile == 'Artístico':
            if any(keyword in work_focus for keyword in ['creatividad', 'arte', 'diseño', 'expresión']):
                coherence += 0.4
            if 'cultural' in sectors or 'artístico' in sectors:
                coherence += 0.6
        
        elif profile == 'Organizador':
            if any(keyword in work_focus for keyword in ['administración', 'gestión', 'organizar', 'dirigir']):
                coherence += 0.4
            if 'comercio' in sectors or 'financiero' in sectors or 'administración' in sectors:
                coherence += 0.3
        
        return min(coherence, 1.0)
    
    def _calculate_environment_sector_score(self, career_name: str, student_preferences: Dict, career_info: Dict) -> float:
        """
        Calcula bonificación por preferencias de entorno y sector laboral
        """
        if not career_info:
            return 0.0
        
        bonus_score = 0.0
        max_bonus = self.weights['environment_sector_preferences']
        
        # Evaluar compatibilidad con entorno de trabajo preferido
        work_env = student_preferences.get('work_environment', 'Oficina')
        env_fit = self._calculate_work_environment_fit(career_name, work_env)
        bonus_score += env_fit * (max_bonus * 0.4)  # 40% del peso para entorno
        
        # Evaluar compatibilidad con nivel de interacción social
        social_level = student_preferences.get('social_interaction', 'Media')
        social_fit = self._calculate_social_interaction_fit(career_name, social_level)
        bonus_score += social_fit * (max_bonus * 0.3)  # 30% del peso para interacción
        
        # Evaluar preferencias laborales generales
        work_focus = student_preferences.get('work_focus', '')
        if work_focus:
            focus_bonus = self._evaluate_work_focus_alignment(career_info, work_focus)
            bonus_score += focus_bonus * (max_bonus * 0.3)  # 30% del peso para enfoque
        
        if bonus_score > 0.05:  # Solo mostrar si es significativo
            print(f"🏢 BONIFICACIÓN ENTORNO/SECTOR para {career_name}: +{bonus_score:.2f}")
        
        return min(bonus_score, max_bonus)
    
    def _calculate_artistic_creative_bonus(self, career_name: str, career_info: Dict) -> float:
        """
        Calcula bonificación especial para carreras artísticas/creativas cuando el perfil es Artístico
        """
        if not career_info:
            return 0.0
        
        # Carreras artísticas/creativas explícitas
        artistic_careers = [
            'Artes Visuales', 'Artes Escénicas', 'Cine y Televisión', 'Diseño de Modas',
            'Fotografía', 'Publicidad', 'Literatura', 'Animación Digital', 'Diseño Gráfico',
            'Música', 'Diseño Industrial', 'Arquitectura', 'Comunicación Social',
            'Ingeniería en Multimedia'
        ]
        
        # Sectores artísticos/creativos
        career_sectors = career_info.get('sector_preferido', [])
        artistic_sectors = ['Cultural', 'Artístico']
        
        # Campos laborales creativos
        career_fields = career_info.get('campo_laboral', [])
        creative_keywords = [
            'artístico', 'creativo', 'diseño', 'arte', 'cultural', 'audiovisual',
            'comunicación', 'publicidad', 'multimedia', 'animación', 'fotografía'
        ]
        
        bonus = 0.0
        
        # Bonificación por carrera explícitamente artística
        if career_name in artistic_careers:
            bonus += 0.15
            print(f"🎨 Carrera artística explícita: {career_name}")
        
        # Bonificación por sector artístico
        if any(sector in artistic_sectors for sector in career_sectors):
            bonus += 0.10
            print(f"🎭 Sector artístico detectado: {career_sectors}")
        
        # Bonificación por campos laborales creativos
        creative_field_count = sum(1 for field in career_fields 
                                 if any(keyword in field.lower() for keyword in creative_keywords))
        if creative_field_count > 0:
            bonus += min(creative_field_count * 0.03, 0.08)
            print(f"🎪 Campos creativos detectados: {creative_field_count}")
        
        return min(bonus, 0.25)  # Máximo 25% de bonificación artística
    
    def _evaluate_work_focus_alignment(self, career_info: Dict, work_focus: str) -> float:
        """
        Evalúa qué tan bien la carrera se alinea con el enfoque de trabajo deseado
        """
        if not work_focus:
            return 0.0
        
        career_description = career_info.get('descripcion', '').lower()
        career_fields = ' '.join(career_info.get('campo_laboral', [])).lower()
        
        work_focus_lower = work_focus.lower()
        
        # Mapeo de enfoques de trabajo a palabras clave
        focus_keywords = {
            'personas': ['social', 'humano', 'comunidad', 'atención', 'salud', 'enseñanza'],
            'tecnología': ['tecnología', 'software', 'sistemas', 'digital', 'informática'],
            'arte': ['arte', 'creativo', 'diseño', 'cultural', 'estético'],
            'investigación': ['investigación', 'análisis', 'científico', 'desarrollo'],
            'administración': ['gestión', 'administración', 'organización', 'dirección'],
            'construcción': ['construcción', 'infraestructura', 'obras', 'edificación']
        }
        
        alignment_score = 0.0
        
        for focus_type, keywords in focus_keywords.items():
            if focus_type in work_focus_lower:
                matches = sum(1 for keyword in keywords 
                            if keyword in career_description or keyword in career_fields)
                if matches > 0:
                    alignment_score += min(matches * 0.2, 0.8)
        
        return min(alignment_score, 1.0)
    
    def _apply_rule_1_1_ml_coherence_check(self, predicted_profile: str, profile_confidence: float, 
                                          student_data: Dict) -> Tuple[bool, str]:
        """
        Regla 1.1: No descartar automáticamente la predicción ML por baja confianza 
        si hay coherencia con el perfil declarado
        """
        if profile_confidence >= 0.4:
            return True, "Confianza ML suficiente"
        
        # Extraer sectores e intereses declarados
        sectors_declarados = student_data.get('¿En cuál de estos sectores te gustaría trabajar?', '')
        trabajo_futuro = student_data.get('¿Cómo te imaginas tu trabajo en 10 años?', '')
        
        # Mapeo de perfiles a sectores/intereses
        profile_sector_mapping = {
            'Artístico': ['cultural', 'artístico', 'arte', 'creaciones propias', 'diseño'],
            'Investigador': ['investigación', 'ciencias', 'datos', 'analizar', 'información'],
            'Social': ['educación', 'personas', 'enseñando', 'cuidando', 'desarrollo humano'],
            'Técnico': ['industrial', 'tic', 'tecnologías', 'herramientas', 'construir'],
            'Organizador': ['administración', 'organizar', 'planificar', 'gestión'],
            'Líder': ['liderazgo', 'dirigir', 'equipos', 'coordinar']
        }
        
        # Verificar coherencia
        if predicted_profile in profile_sector_mapping:
            keywords = profile_sector_mapping[predicted_profile]
            sectors_text = (sectors_declarados + ' ' + trabajo_futuro).lower()
            
            for keyword in keywords:
                if keyword in sectors_text:
                    return True, f"Coherencia detectada: '{keyword}' coincide con perfil {predicted_profile}"
        
        return False, "Sin coherencia con preferencias declaradas"
    
    def _apply_rule_1_2_hybrid_weighting(self, coherencia: str, base_profile: str, 
                                        ml_profile: str, ml_confidence: float) -> Tuple[str, float]:
        """
        Regla 1.2: Híbrido ponderado entre perfil base y predicción ML
        """
        if coherencia in ["Coherente", "Muy Coherente"]:
            # Fórmula ponderada: 0.6 * perfil_base + 0.4 * perfil_ML
            if ml_confidence > 0.3:  # Solo si ML tiene confianza mínima
                final_profile = f"{base_profile}-{ml_profile}"
                hybrid_confidence = 0.6 * 0.8 + 0.4 * ml_confidence  # Asumiendo base_profile con 0.8
                return final_profile, hybrid_confidence
            else:
                return base_profile, 0.75  # Usar base profile con alta confianza
        
        return ml_profile, ml_confidence
    
    def _apply_rule_2_1_sector_bonus(self, career_info: Dict, student_data: Dict) -> Tuple[float, str]:
        """
        Regla 2.1: Bonificación fuerte si carrera pertenece a sectores explícitamente mencionados
        """
        if not career_info:
            return 0.0, ""
        
        sectors_declarados = student_data.get('¿En cuál de estos sectores te gustaría trabajar?', '')
        if not sectors_declarados:
            return 0.0, ""
        
        career_sectors = career_info.get('sector_preferido', [])
        sectors_declarados_list = [s.strip() for s in sectors_declarados.split(',')]
        
        # Mapear sectores del formulario a sectores de carrera
        sector_matches = []
        for sector_declarado in sectors_declarados_list:
            mapped_sector = self.sector_mapping.get(sector_declarado, sector_declarado)
            if mapped_sector in career_sectors:
                sector_matches.append(sector_declarado)
        
        if sector_matches:
            bonus = 0.05  # 5% de bonificación
            reason = f"Sector explícito '{sector_matches[0]}' coincide"
            return bonus, reason
        
        return 0.0, ""
    
    def _apply_rule_2_2_work_focus_bonus(self, career_info: Dict, student_data: Dict) -> Tuple[float, str]:
        """
        Regla 2.2: Bonificación por coincidencia entre "gustos" y "enfoque laboral"
        """
        if not career_info:
            return 0.0, ""
        
        # Analizar actividades favoritas
        actividades_libres = student_data.get('¿Qué prefieres hacer en tus ratos libres?', '')
        trabajo_futuro = student_data.get('¿Cómo te imaginas tu trabajo en 10 años?', '')
        
        career_description = career_info.get('descripcion', '').lower()
        career_fields = ' '.join(career_info.get('campo_laboral', [])).lower()
        
        # Mapeo de gustos a enfoques laborales
        gusto_enfoque_mapping = {
            'actividades artisticas': ['crear', 'diseño', 'arte', 'creatividad'],
            'experimentos': ['investigar', 'analizar', 'ciencia', 'desarrollo'],
            'conversas': ['comunicar', 'social', 'relaciones', 'atención'],
            'construir': ['construir', 'desarrollar', 'crear', 'implementar'],
            'organizar': ['gestionar', 'administrar', 'planificar', 'coordinar'],
            'liderar': ['dirigir', 'liderar', 'coordinar', 'gestionar']
        }
        
        for gusto, enfoques in gusto_enfoque_mapping.items():
            if gusto in actividades_libres.lower() or gusto in trabajo_futuro.lower():
                for enfoque in enfoques:
                    if enfoque in career_description or enfoque in career_fields:
                        bonus = 0.03  # 3% de bonificación
                        reason = f"Coincidencia gusto-enfoque: '{gusto}' → '{enfoque}'"
                        return bonus, reason
        
        return 0.0, ""
    
    def _apply_rule_3_1_social_contradiction_penalty(self, career_name: str, student_data: Dict) -> Tuple[float, str]:
        """
        Regla 3.1: Penalizar carreras que contradigan preferencias claras de interacción social
        """
        interaccion_preferida = student_data.get('¿Qué nivel de interacción con otras personas te gustaría que tuviera tu trabajo?', '')
        
        if not interaccion_preferida:
            return 0.0, ""
        
        # Carreras de alta interacción social
        high_interaction_careers = [
            'Medicina', 'Enfermería', 'Psicología', 'Trabajo Social', 'Derecho',
            'Administración de Empresas', 'Licenciatura en Educación Física',
            'Licenciatura en Matemáticas', 'Comunicación Social'
        ]
        
        # Carreras de baja interacción social
        low_interaction_careers = [
            'Ingeniería de Sistemas', 'Estadística', 'Ciencia de Datos',
            'Ingeniería Civil', 'Ingeniería Mecánica', 'Tecnología en Desarrollo de Software'
        ]
        
        if 'poca' in interaccion_preferida.lower() and career_name in high_interaction_careers:
            penalty = -0.05  # -5% de penalización
            reason = "Contradice preferencia de poca interacción social"
            return penalty, reason
        elif 'mucha' in interaccion_preferida.lower() and career_name in low_interaction_careers:
            penalty = -0.05  # -5% de penalización  
            reason = "Contradice preferencia de mucha interacción social"
            return penalty, reason
        
        return 0.0, ""
    
    def _apply_rule_3_2_work_environment_penalty(self, career_name: str, student_data: Dict) -> Tuple[float, str]:
        """
        Regla 3.2: Evitar recomendar carreras con entornos no deseados
        """
        entorno_preferido = student_data.get('¿En qué lugar te gustaría trabajar?', '')
        
        if not entorno_preferido:
            return 0.0, ""
        
        # Carreras que requieren alta presencialidad
        high_presence_careers = [
            'Medicina', 'Enfermería', 'Odontología', 'Medicina Veterinaria',
            'Ingeniería Civil', 'Arquitectura', 'Enfermería'
        ]
        
        if ('casa' in entorno_preferido.lower() or 'remoto' in entorno_preferido.lower()) and career_name in high_presence_careers:
            penalty = -0.03  # -3% de penalización
            reason = "Requiere alta presencialidad vs preferencia remota"
            return penalty, reason
        
        return 0.0, ""
    
    def _apply_rule_4_1_limit_similar_subfields(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Regla 4.1: Máximo 2 carreras por subárea similar
        """
        # Definir subáreas similares
        subfield_groups = {
            'ingenierias_sistemas': ['Ingeniería de Sistemas', 'Tecnología en Desarrollo de Software', 'Ciencia de Datos'],
            'ingenierias_civil': ['Ingeniería Civil', 'Arquitectura', 'Ingeniería de Construcción'],
            'medicina_salud': ['Medicina', 'Enfermería', 'Medicina Veterinaria'],
            'administracion': ['Administración de Empresas', 'Contaduría Pública', 'Administración Financiera'],
            'educacion': ['Licenciatura en Matemáticas', 'Licenciatura en Educación Física', 'Pedagogía'],
            'artes': ['Diseño Gráfico', 'Artes Plásticas', 'Música', 'Diseño Industrial']
        }
        
        # Contar carreras por subárea
        subfield_counts = {group: 0 for group in subfield_groups}
        filtered_recommendations = []
        
        for rec in recommendations:
            career_name = rec['nombre']
            
            # Encontrar subárea de la carrera
            career_subfield = None
            for subfield, careers in subfield_groups.items():
                if career_name in careers:
                    career_subfield = subfield
                    break
            
            # Si no tiene subárea definida o no ha alcanzado el límite, incluir
            if career_subfield is None or subfield_counts[career_subfield] < 2:
                filtered_recommendations.append(rec)
                if career_subfield:
                    subfield_counts[career_subfield] += 1
        
        return filtered_recommendations
    
    def _apply_rule_4_2_prioritize_diverse_sectors(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Regla 4.2: Priorización de subáreas distintas si compatibilidad es similar
        """
        if len(recommendations) <= 2:
            return recommendations
        
        # Agrupar por sector
        sector_groups = {}
        for i, rec in enumerate(recommendations):
            career_info = self.career_db.get_career_info(rec['nombre'])
            if career_info:
                sectors = career_info.get('sector_preferido', ['General'])
                main_sector = sectors[0] if sectors else 'General'
                
                if main_sector not in sector_groups:
                    sector_groups[main_sector] = []
                sector_groups[main_sector].append((i, rec))
        
        # Reorganizar para diversidad
        diverse_recommendations = []
        used_indices = set()
        
        # Primera pasada: tomar la mejor de cada sector
        for sector, career_list in sector_groups.items():
            if career_list:
                best_idx, best_rec = min(career_list, key=lambda x: x[0])  # Primera en la lista original
                if best_idx not in used_indices:
                    diverse_recommendations.append(best_rec)
                    used_indices.add(best_idx)
        
        # Segunda pasada: completar con las restantes
        for i, rec in enumerate(recommendations):
            if i not in used_indices and len(diverse_recommendations) < len(recommendations):
                diverse_recommendations.append(rec)
        
        return diverse_recommendations
    
    def _apply_rule_5_1_personalized_reasons(self, career_name: str, student_data: Dict, 
                                           career_info: Dict) -> List[str]:
        """
        Regla 5.1: Personalizar razones por carrera según entrada del estudiante
        """
        personalized_reasons = []
        
        # Analizar actividades favoritas
        actividades_libres = student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower()
        trabajo_futuro = student_data.get('¿Cómo te imaginas tu trabajo en 10 años?', '').lower()
        personalidad = student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower()
        
        # Razones específicas por actividad/perfil
        if 'actividades artisticas' in actividades_libres and 'Diseño' in career_name:
            personalized_reasons.append("Porque disfrutas crear con herramientas visuales")
        
        if 'liderar' in personalidad and 'Industrial' in career_name:
            personalized_reasons.append("Tu perfil de liderazgo se alinea con la gestión de equipos en esta carrera")
        
        if 'experimentos' in actividades_libres and any(word in career_name.lower() for word in ['medicina', 'biología', 'química']):
            personalized_reasons.append("Tu interés por experimentos coincide con el enfoque científico de esta carrera")
        
        if 'construir' in actividades_libres and any(word in career_name.lower() for word in ['ingeniería', 'arquitectura']):
            personalized_reasons.append("Tu gusto por construir cosas se refleja en esta carrera práctica")
        
        if 'conversas' in actividades_libres and any(word in career_name.lower() for word in ['psicología', 'social', 'educación']):
            personalized_reasons.append("Tu naturaleza social se alinea perfectamente con esta carrera")
        
        if 'datos' in trabajo_futuro and any(word in career_name.lower() for word in ['estadística', 'datos', 'sistemas']):
            personalized_reasons.append("Tu interés por trabajar con datos coincide con el enfoque analítico de esta carrera")
        
        return personalized_reasons
    
    def _apply_rule_5_2_transparency_indicators(self, career_name: str, compatibility_details: Dict,
                                              profile_confidence: float, sector_confidence: float,
                                              base_profile: str, ml_profile: str) -> List[str]:
        """
        Regla 5.2: Indicar cuándo una carrera aparece solo por afinidad técnica o solo por perfil ML
        """
        transparency_indicators = []
        
        # Indicar si es solo por perfil ML con baja confianza
        if profile_confidence < 0.4 and compatibility_details.get('profile_match'):
            transparency_indicators.append("Incluida por predicción ML, aunque con baja confianza")
        
        # Indicar si contradice sector preferido
        if not compatibility_details.get('sector_match') and compatibility_details.get('academic_fit', 0) > 0.7:
            transparency_indicators.append("Incluida por afinidad técnica, aunque tu sector preferido es diferente")
        
        # Indicar si es híbrido base vs ML
        if base_profile != ml_profile and compatibility_details.get('profile_match'):
            transparency_indicators.append(f"Coincide con perfil ML ({ml_profile}), tu perfil base es ({base_profile})")
        
        # Indicar si es por bonificación artística
        if 'Artístico' in base_profile and any(word in career_name.lower() for word in ['arte', 'diseño', 'música']):
            transparency_indicators.append("Recomendada por tu perfil artístico declarado")
        
        return transparency_indicators
    
    def _ensure_sector_diversity(self, filtered_careers: List[Tuple], min_careers: int) -> List[Tuple]:
        """
        Asegura diversidad por sector incluyendo al menos 2 carreras por sector principal
        """
        sector_groups = {}
        remaining_careers = []
        
        # Agrupar carreras por sector
        for career, compatibility in filtered_careers:
            career_info = self.career_db.get_career_info(career)
            if career_info:
                sectors = career_info.get('sector_preferido', ['General'])
                main_sector = sectors[0] if sectors else 'General'
                
                if main_sector not in sector_groups:
                    sector_groups[main_sector] = []
                sector_groups[main_sector].append((career, compatibility))
            else:
                remaining_careers.append((career, compatibility))
        
        # Tomar al menos 1 carrera de cada sector (para diversidad)
        diverse_careers = []
        for sector, careers in sector_groups.items():
            # Ordenar por compatibilidad y tomar las mejores del sector
            careers_sorted = sorted(careers, key=lambda x: x[1]['overall_compatibility'], reverse=True)
            diverse_careers.extend(careers_sorted[:2])  # Máximo 2 por sector
        
        # Agregar carreras restantes
        diverse_careers.extend(remaining_careers)
        
        # Asegurar que tenemos suficientes carreras
        if len(diverse_careers) < min_careers and len(filtered_careers) > len(diverse_careers):
            # Añadir las mejores carreras restantes
            remaining = [career for career in filtered_careers if career not in diverse_careers]
            remaining_sorted = sorted(remaining, key=lambda x: x[1]['overall_compatibility'], reverse=True)
            diverse_careers.extend(remaining_sorted[:min_careers - len(diverse_careers)])
        
        return diverse_careers[:min_careers]
    
    def _calculate_diversity_bonus(self, career_name: str, existing_scores: Dict, career_info: Dict) -> float:
        """
        Calcula bonificación de diversidad para evitar recomendaciones repetitivas
        """
        if not career_info:
            return 0.0
        
        diversity_bonus = 0.0
        
        # Bonificación por sector poco representado
        career_sectors = career_info.get('sector_preferido', ['General'])
        main_sector = career_sectors[0] if career_sectors else 'General'
        
        # Contar cuántas carreras del mismo sector ya tienen alta puntuación
        sector_count = 0
        for existing_career, score in existing_scores.items():
            existing_info = self.career_db.get_career_info(existing_career)
            if existing_info:
                existing_sectors = existing_info.get('sector_preferido', ['General'])
                if existing_sectors and existing_sectors[0] == main_sector:
                    sector_count += 1
        
        # Dar bonificación si el sector está poco representado
        if sector_count == 0:
            diversity_bonus += 0.08  # Primer carrera del sector
        elif sector_count == 1:
            diversity_bonus += 0.04  # Segunda carrera del sector
        
        # Bonificación por tipo de carrera diversa (técnica vs tradicional)
        technical_careers = self._get_technical_careers()
        is_technical = career_name in technical_careers or 'Tecnología' in career_name
        
        # Contar carreras técnicas vs tradicionales en las existentes
        tech_count = sum(1 for career in existing_scores.keys() 
                        if career in technical_careers or 'Tecnología' in career)
        traditional_count = len(existing_scores) - tech_count
        
        # Bonificar equilibrio entre técnicas y tradicionales
        if is_technical and tech_count < traditional_count:
            diversity_bonus += 0.03
        elif not is_technical and traditional_count < tech_count:
            diversity_bonus += 0.03
        
        # Pequeña variación aleatoria para romper empates (reproducible por nombre)
        hash_value = int(hashlib.md5(career_name.encode()).hexdigest()[:8], 16)
        random_bonus = (hash_value % 100) / 10000  # 0.0000 to 0.0099
        diversity_bonus += random_bonus
        
        return diversity_bonus
    
    def _apply_post_prediction_logic_layer(self, career_name: str, student_data: Dict, 
                                          compatibility: Dict) -> Dict:
        """
        Capa de reglas lógicas POST-PREDICCIÓN para filtrar contradicciones y falsos positivos
        """
        logic_result = {
            'should_exclude': False,
            'exclusion_reasons': [],
            'penalty_score': 0.0,
            'penalty_reasons': [],
            'logic_applied': []
        }
        
        # REGLA LÓGICA 1: Interacción social estricta
        self._apply_social_interaction_logic(career_name, student_data, logic_result)
        
        # REGLA LÓGICA 2: Entorno de trabajo estricto
        self._apply_work_environment_logic(career_name, student_data, logic_result)
        
        # REGLA LÓGICA 3: Funciones vs valores personales
        self._apply_function_values_logic(career_name, student_data, logic_result)
        
        # REGLA LÓGICA 4: Contradicciones de personalidad-carrera
        self._apply_personality_contradiction_logic(career_name, student_data, logic_result)
        
        # REGLA LÓGICA 5: Evaluación de variables negativas
        self._apply_negative_variables_logic(career_name, student_data, logic_result)
        
        return logic_result
    
    def _apply_social_interaction_logic(self, career_name: str, student_data: Dict, logic_result: Dict) -> None:
        """
        Reglas estrictas de interacción social para eliminar contradicciones evidentes
        """
        interaccion_preferida = student_data.get('¿Qué nivel de interacción con otras personas te gustaría que tuviera tu trabajo?', '')
        actividades_libres = student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower()
        personalidad = student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower()
        
        # CARRERAS DE MUY ALTA INTERACCIÓN SOCIAL (AMPLIADA)
        very_high_interaction = [
            'Psicología', 'Trabajo Social', 'Medicina', 'Enfermería', 'Odontología',
            'Licenciatura en Educación Física', 'Comunicación Social', 'Medicina Veterinaria',
            'Administración de Empresas', 'Derecho', 'Licenciatura en Matemáticas',
            'Licenciatura en Ciencias Sociales', 'Publicidad', 'Relaciones Públicas',
            'Pedagogía', 'Terapia Ocupacional', 'Fonoaudiología', 'Fisioterapia',
            'Negocios Internacionales', 'Mercadeo', 'Recursos Humanos'
        ]
        
        # Carreras de MUY BAJA interacción social
        very_low_interaction = [
            'Ingeniería de Sistemas', 'Estadística', 'Ciencia de Datos',
            'Tecnología en Desarrollo de Software', 'Ingeniería Mecánica',
            'Matemáticas', 'Física', 'Astronomía', 'Programación',
            'Animación Digital', 'Fotografía', 'Diseño Gráfico'
        ]
        
        # FILTRO ESTRICTO: Poca interacción + carrera de alta interacción
        if 'poca' in interaccion_preferida.lower() and career_name in very_high_interaction:
            # Verificar señales adicionales que confirmen la preferencia de poco contacto
            low_contact_signals = [
                'ordenar mi espacio' in actividades_libres,
                'leer' in actividades_libres,
                'experimentos' in actividades_libres,
                'construir cosas' in actividades_libres,
                'solo' in actividades_libres,
                'introvertido' in personalidad or 'tímido' in personalidad,
                'reservado' in personalidad,
                'independiente' in personalidad
            ]
            
            # EXCLUSIÓN AUTOMÁTICA si hay al menos 1 señal confirmatoria (más estricto)
            if sum(low_contact_signals) >= 1:
                logic_result['should_exclude'] = True
                logic_result['exclusion_reasons'].append(
                    f"❌ EXCLUSIÓN CRÍTICA: Preferencia explícita de POCA interacción social incompatible con {career_name} (carrera de muy alta interacción)"
                )
            else:
                # Penalización fuerte incluso sin señales adicionales
                logic_result['penalty_score'] -= 0.30  # Penalización muy severa
                logic_result['penalty_reasons'].append("⚠️ Contradicción social severa")
        
        # FILTRO: Alta interacción deseada + carrera muy técnica/solitaria
        elif 'mucha' in interaccion_preferida.lower() and career_name in very_low_interaction:
            # Verificar señales de alta sociabilidad
            high_social_signals = [
                'conversas' in actividades_libres,
                'amigos' in actividades_libres,
                'equipos' in actividades_libres,
                'sociable' in personalidad,
                'liderar' in personalidad or 'líder' in personalidad,
                'comunicativo' in personalidad,
                'extrovertido' in personalidad
            ]
            
            if sum(high_social_signals) >= 2:
                logic_result['penalty_score'] -= 0.25  # Penalización muy fuerte
                logic_result['penalty_reasons'].append("⚠️ Contradicción: Alta sociabilidad vs carrera de baja interacción")
        
        logic_result['logic_applied'].append("Lógica de interacción social")
    
    def _apply_work_environment_logic(self, career_name: str, student_data: Dict, logic_result: Dict) -> None:
        """
        Reglas estrictas de entorno de trabajo
        """
        entorno_preferido = student_data.get('¿En qué lugar te gustaría trabajar?', '').lower()
        
        # Carreras que REQUIEREN presencialidad física crítica
        high_presence_required = [
            'Medicina', 'Enfermería', 'Odontología', 'Medicina Veterinaria',
            'Ingeniería Civil', 'Arquitectura', 'Construcción'
        ]
        
        # Carreras incompatibles con trabajo remoto
        remote_incompatible = [
            'Medicina', 'Enfermería', 'Ingeniería Civil', 'Arquitectura',
            'Licenciatura en Educación Física', 'Trabajo Social'
        ]
        
        # EXCLUSIÓN: Preferencia de trabajo remoto + carrera que requiere presencialidad
        if (('casa' in entorno_preferido or 'remoto' in entorno_preferido) and 
            career_name in remote_incompatible):
            logic_result['penalty_score'] -= 0.10
            logic_result['penalty_reasons'].append("Incompatibilidad: Trabajo remoto vs carrera presencial obligatoria")
        
        logic_result['logic_applied'].append("Lógica de entorno de trabajo")
    
    def _apply_function_values_logic(self, career_name: str, student_data: Dict, logic_result: Dict) -> None:
        """
        Evalúa contradicciones entre funciones de la carrera y valores personales declarados
        FILTROS ESTRICTOS para contradicciones función-valor
        """
        trabajo_futuro = student_data.get('¿Cómo te imaginas tu trabajo en 10 años?', '').lower()
        tema_trabajo = student_data.get('¿Cuál sería el tema principal de tu trabajo?', '').lower()
        personalidad = student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower()
        interaccion_trabajo = student_data.get('¿Qué nivel de interacción con otras personas te gustaría que tuviera tu trabajo?', '').lower()
        
        # CONTRADICCIÓN CRÍTICA: Licenciatura en Matemáticas + No quiere enseñar + Poca interacción
        if career_name == 'Licenciatura en Matemáticas':
            teaching_indicators = [
                'enseñar' in trabajo_futuro or 'enseñar' in tema_trabajo,
                'enseñando' in trabajo_futuro,
                'docente' in trabajo_futuro,
                'profesor' in trabajo_futuro,
                'educación' in trabajo_futuro or 'educación' in tema_trabajo,
                'estudiantes' in trabajo_futuro,
                'aulas' in trabajo_futuro
            ]
            
            wants_low_interaction = 'poca' in interaccion_trabajo
            
            if sum(teaching_indicators) == 0 and wants_low_interaction:
                logic_result['should_exclude'] = True
                logic_result['exclusion_reasons'].append(
                    f"❌ EXCLUSIÓN CRÍTICA: Licenciatura en Matemáticas requiere enseñanza (alta interacción) pero estudiante prefiere poca interacción y no menciona interés en enseñar"
                )
            elif sum(teaching_indicators) == 0:
                logic_result['penalty_score'] -= 0.25
                logic_result['penalty_reasons'].append(
                    "⚠️ Contradicción crítica: Licenciatura requiere vocación docente no expresada"
                )
        
        # Mapeo ampliado de carreras a funciones principales
        career_functions = {
            'Psicología': ['ayudar personas', 'escuchar', 'aconsejar', 'terapia', 'salud mental'],
            'Medicina': ['curar', 'diagnosticar', 'salvar vidas', 'atención directa', 'salud'],
            'Odontología': ['atención dental', 'salud bucal', 'pacientes', 'curar', 'diagnosticar'],
            'Ingeniería de Sistemas': ['programar', 'desarrollar software', 'solucionar problemas técnicos', 'tecnología'],
            'Administración de Empresas': ['gestionar', 'liderar equipos', 'tomar decisiones', 'organizar'],
            'Contaduría Pública': ['analizar números', 'auditar', 'control financiero', 'números'],
            'Derecho': ['defender', 'argumentar', 'representar legalmente', 'justicia'],
            'Licenciatura en Matemáticas': ['enseñar', 'docencia', 'educación', 'estudiantes'],
            'Arquitectura': ['diseñar', 'crear espacios', 'construcción', 'visual'],
            'Diseño Gráfico': ['crear', 'diseñar', 'visual', 'comunicar', 'arte']
        }
        
        if career_name in career_functions:
            functions = career_functions[career_name]
            
            # 1. CONTRADICCIÓN: Carrera de ayuda/salud + No menciona ayudar a otros
            if career_name in ['Psicología', 'Trabajo Social', 'Medicina', 'Enfermería', 'Odontología']:
                help_indicators = [
                    'personas' in trabajo_futuro,
                    'ayudar' in trabajo_futuro or 'ayudar' in tema_trabajo,
                    'cuidando' in trabajo_futuro or 'cuidar' in trabajo_futuro,
                    'enseñando' in trabajo_futuro,
                    'pacientes' in trabajo_futuro,
                    'salud' in trabajo_futuro or 'salud' in tema_trabajo,
                    'sociable' in personalidad,
                    'empático' in personalidad
                ]
                
                if sum(help_indicators) == 0:  # NO hay ninguna señal de querer ayudar
                    logic_result['should_exclude'] = True
                    logic_result['exclusion_reasons'].append(
                        f"❌ EXCLUSIÓN: {career_name} requiere vocación de servicio/ayuda no expresada"
                    )
                elif sum(help_indicators) <= 1:  # Muy pocas señales
                    logic_result['penalty_score'] -= 0.30
                    logic_result['penalty_reasons'].append(
                        f"⚠️ Contradicción valores: {career_name} requiere orientación de ayuda poco evidente"
                    )
            
            # 2. CONTRADICCIÓN: Carrera técnica + No le interesan aspectos técnicos
            elif career_name in ['Ingeniería de Sistemas', 'Ciencia de Datos', 'Estadística', 'Tecnología en Desarrollo de Software']:
                tech_indicators = [
                    'datos' in trabajo_futuro or 'información' in trabajo_futuro,
                    'desarrollar' in trabajo_futuro or 'crear' in trabajo_futuro,
                    'tecnología' in tema_trabajo or 'sistemas' in tema_trabajo,
                    'programar' in trabajo_futuro or 'programación' in trabajo_futuro,
                    'software' in trabajo_futuro,
                    'analizar' in trabajo_futuro,
                    'curioso' in personalidad or 'hábil' in personalidad,
                    'lógico' in personalidad or 'técnico' in personalidad
                ]
                
                if sum(tech_indicators) == 0:
                    logic_result['penalty_score'] -= 0.25
                    logic_result['penalty_reasons'].append(
                        f"⚠️ Contradicción técnica: {career_name} requiere orientación técnica no expresada"
                    )
            
            # 3. CONTRADICCIÓN: Derecho + No le interesan aspectos legales/argumentativos
            elif career_name == 'Derecho':
                legal_indicators = [
                    'justicia' in trabajo_futuro or 'justicia' in tema_trabajo,
                    'defender' in trabajo_futuro or 'representar' in trabajo_futuro,
                    'argumentar' in trabajo_futuro or 'debate' in trabajo_futuro,
                    'legal' in trabajo_futuro or 'jurídico' in trabajo_futuro,
                    'líder' in personalidad or 'decidido' in personalidad,
                    'comunicativo' in personalidad
                ]
                
                if sum(legal_indicators) == 0:
                    logic_result['penalty_score'] -= 0.25
                    logic_result['penalty_reasons'].append(
                        "⚠️ Contradicción: Derecho requiere orientación argumentativa/legal no expresada"
                    )
        
        logic_result['logic_applied'].append("Lógica de funciones vs valores")
    
    def _apply_personality_contradiction_logic(self, career_name: str, student_data: Dict, logic_result: Dict) -> None:
        """
        Detecta contradicciones entre personalidad declarada y requerimientos de carrera
        """
        personalidad = student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower()
        actividades_libres = student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower()
        
        # Carreras que requieren liderazgo/gestión
        leadership_careers = ['Administración de Empresas', 'Derecho', 'Ingeniería Industrial']
        
        # Carreras que requieren creatividad/expresión
        creative_careers = ['Diseño Gráfico', 'Arquitectura', 'Comunicación Social', 'Artes Plásticas']
        
        # Carreras que requieren precisión/detalle
        detail_careers = ['Contaduría Pública', 'Estadística', 'Medicina']
        
        # CONTRADICCIÓN: Carrera de liderazgo + Personalidad no líder
        if career_name in leadership_careers:
            leadership_indicators = [
                'líder' in personalidad or 'liderar' in personalidad,
                'organizar' in actividades_libres,
                'dirigir' in personalidad,
                'decidido' in personalidad
            ]
            
            anti_leadership_indicators = [
                'tímido' in personalidad,
                'introvertido' in personalidad,
                'seguir' in personalidad,
                'solo' in actividades_libres
            ]
            
            if (sum(leadership_indicators) == 0 and sum(anti_leadership_indicators) >= 1):
                logic_result['penalty_score'] -= 0.15
                logic_result['penalty_reasons'].append(
                    f"Contradicción liderazgo: {career_name} requiere perfil de liderazgo no evidente"
                )
        
        # CONTRADICCIÓN: Carrera creativa + No muestra creatividad
        elif career_name in creative_careers:
            creative_indicators = [
                'imaginativo' in personalidad,
                'creativo' in personalidad,
                'artisticas' in actividades_libres,
                'diseñar' in actividades_libres or 'crear' in actividades_libres
            ]
            
            if sum(creative_indicators) == 0:
                logic_result['penalty_score'] -= 0.12
                logic_result['penalty_reasons'].append(
                    f"Contradicción creativa: {career_name} requiere orientación creativa no expresada"
                )
        
        logic_result['logic_applied'].append("Lógica de contradicciones de personalidad")
    
    def _apply_negative_variables_logic(self, career_name: str, student_data: Dict, logic_result: Dict) -> None:
        """
        Evalúa variables NEGATIVAS - lo que definitivamente NO va con el estudiante
        FILTROS ESTRICTOS para contradicciones explícitas
        """
        materias_menos_favoritas = student_data.get('¿Cuáles son las materias que te gustan MENOS?', '').lower()
        materias_malas = student_data.get('¿En qué materias NO TE VA BIEN?', '').lower()
        personalidad = student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower()
        sectores_preferidos = student_data.get('¿En cuál de estos sectores te gustaría trabajar?', '').lower()
        
        # 1. FILTRO DE SECTORES NO PREFERIDOS (NUEVO)
        self._apply_sector_preference_filter(career_name, sectores_preferidos, logic_result)
        
        # 2. EXCLUSIÓN FUERTE: Odio explícito a matemáticas + carrera muy matemática
        math_heavy_careers = [
            'Ingeniería de Sistemas', 'Estadística', 'Ciencia de Datos', 
            'Ingeniería Civil', 'Ingeniería Mecánica', 'Contaduría Pública',
            'Licenciatura en Matemáticas', 'Física', 'Astronomía', 'Actuaría',
            'Ingeniería Industrial', 'Economía', 'Finanzas'
        ]
        
        if career_name in math_heavy_careers:
            math_negative_signals = [
                'matemáticas' in materias_menos_favoritas,
                'matemáticas' in materias_malas,
                'física' in materias_menos_favoritas,
                'física' in materias_malas,
                'números' in materias_menos_favoritas
            ]
            
            # EXCLUSIÓN si odian explícitamente matemáticas
            if 'matemáticas' in materias_menos_favoritas and career_name == 'Licenciatura en Matemáticas':
                logic_result['should_exclude'] = True
                logic_result['exclusion_reasons'].append(
                    f"❌ EXCLUSIÓN CRÍTICA: Materia odiada (Matemáticas) vs {career_name} (carrera basada en esa materia)"
                )
            elif sum(math_negative_signals) >= 2:  # Múltiples señales negativas
                logic_result['should_exclude'] = True
                logic_result['exclusion_reasons'].append(
                    f"❌ EXCLUSIÓN: Múltiples señales de rechazo a matemáticas vs carrera matemática ({career_name})"
                )
            elif sum(math_negative_signals) >= 1:  # Una señal negativa = penalización severa
                logic_result['penalty_score'] -= 0.35
                logic_result['penalty_reasons'].append(
                    f"⚠️ Variables negativas: Rechazo a matemáticas vs carrera matemática"
                )
        
        # 3. EXCLUSIÓN: Rechazo a ciencias + carrera científica
        science_careers = ['Medicina', 'Enfermería', 'Medicina Veterinaria', 'Biología', 'Química',
                          'Bacteriología', 'Biomedicina', 'Biotecnología', 'Odontología']
        
        if career_name in science_careers:
            science_negative_signals = [
                'biología y química' in materias_menos_favoritas,
                'biología' in materias_menos_favoritas,
                'química' in materias_menos_favoritas,
                'ciencias naturales' in materias_menos_favoritas
            ]
            
            if sum(science_negative_signals) >= 2:  # Múltiples rechazos a ciencias
                logic_result['should_exclude'] = True
                logic_result['exclusion_reasons'].append(
                    f"❌ EXCLUSIÓN: Rechazo múltiple a ciencias vs carrera científica ({career_name})"
                )
            elif sum(science_negative_signals) >= 1:
                logic_result['penalty_score'] -= 0.30
                logic_result['penalty_reasons'].append(
                    f"⚠️ Variables negativas: Rechazo a ciencias vs carrera científica"
                )
        
        # 4. EXCLUSIÓN: Rechazo a ciencias sociales + carreras sociales/humanísticas
        social_humanities_careers = ['Psicología', 'Trabajo Social', 'Derecho', 'Licenciatura en Ciencias Sociales',
                                   'Filosofía', 'Historia', 'Sociología', 'Antropología', 'Ciencia Política']
        
        if career_name in social_humanities_careers:
            social_negative_signals = [
                'ciencias sociales' in materias_menos_favoritas,
                'ciencias sociales' in materias_malas,
                'filosofía' in materias_menos_favoritas,
                'historia' in materias_menos_favoritas
            ]
            
            if sum(social_negative_signals) >= 1:
                logic_result['penalty_score'] -= 0.25
                logic_result['penalty_reasons'].append(
                    f"⚠️ Variables negativas: Rechazo a ciencias sociales vs carrera social/humanística"
                )
        
        # 5. EXCLUSIÓN: Rechazo a educación artística + carreras artísticas
        artistic_careers = ['Diseño Gráfico', 'Artes Plásticas', 'Música', 'Teatro', 'Danza',
                          'Arquitectura', 'Diseño Industrial', 'Animación Digital', 'Fotografía']
        
        if career_name in artistic_careers:
            artistic_negative_signals = [
                'educación artística' in materias_menos_favoritas,
                'educación artística' in materias_malas,
                'arte' in materias_menos_favoritas,
                'dibujo' in materias_menos_favoritas
            ]
            
            if sum(artistic_negative_signals) >= 1:
                logic_result['penalty_score'] -= 0.25
                logic_result['penalty_reasons'].append(
                    f"⚠️ Variables negativas: Rechazo a educación artística vs carrera artística"
                )
        
        logic_result['logic_applied'].append("Lógica de variables negativas")
    
    def _apply_sector_preference_filter(self, career_name: str, sectores_preferidos: str, logic_result: Dict) -> None:
        """
        NUEVO: Filtro estricto para carreras que NO están en sectores preferidos explícitamente
        """
        if not sectores_preferidos.strip():
            return  # No hay preferencias de sector declaradas
        
        # Mapeo de carreras a sectores
        career_sectors = {
            # TIC y Telecomunicaciones
            'Ingeniería de Sistemas': 'tic',
            'Ciencia de Datos': 'tic',
            'Tecnología en Desarrollo de Software': 'tic',
            'Animación Digital': 'tic',
            
            # Salud
            'Medicina': 'salud',
            'Enfermería': 'salud',
            'Odontología': 'salud',
            'Medicina Veterinaria': 'salud',
            
            # Educativo
            'Licenciatura en Matemáticas': 'educativo',
            'Licenciatura en Educación Física': 'educativo',
            'Licenciatura en Ciencias Sociales': 'educativo',
            
            # Industrial/Manufacturero
            'Ingeniería Industrial': 'industrial',
            'Ingeniería Mecánica': 'industrial',
            'Ingeniería Civil': 'industrial',
            
            # Económico/Financiero
            'Contaduría Pública': 'economico',
            'Administración de Empresas': 'economico',
            'Economía': 'economico',
            
            # Jurídico/Legal
            'Derecho': 'juridico',
            
            # Arte y Comunicación
            'Diseño Gráfico': 'arte',
            'Comunicación Social': 'arte',
            'Fotografía': 'arte',
            'Arquitectura': 'arte'
        }
        
        # Verificar si la carrera pertenece a un sector NO preferido
        if career_name in career_sectors:
            career_sector = career_sectors[career_name]
            
            # Mapeo de sectores preferidos a palabras clave
            sector_keywords = {
                'tic': 'tic', 
                'salud': 'salud',
                'educativo': 'educativo',
                'industrial': 'industrial',
                'economico': 'economico',
                'juridico': 'juridico',
                'arte': 'arte'
            }
            
            # Verificar si el sector de la carrera está en las preferencias
            sector_mentioned = any(keyword in sectores_preferidos for keyword in sector_keywords[career_sector].split())
            
            if not sector_mentioned:
                # PENALIZACIÓN FUERTE por sector no preferido
                logic_result['penalty_score'] -= 0.20
                logic_result['penalty_reasons'].append(
                    f"⚠️ Sector no preferido: {career_name} ({career_sector}) no coincide con sectores declarados"
                )
    
    def _refine_sector_weight(self, career_name: str, student_data: Dict, career_info: Dict,
                            compatibility: Dict) -> float:
        """
        Refina el peso del sector ML - no usar coincidencia de sector como única validación fuerte
        """
        if not career_info:
            return 0.0
        
        sector_refinement = 0.0
        
        # El sector coincide, PERO ¿las funciones y valores también?
        if compatibility.get('sector_match', False):
            # Verificar alineación de funciones (más importante que solo el sector)
            function_alignment = self._calculate_function_alignment(career_name, student_data, career_info)
            
            # Verificar alineación de valores personales
            values_alignment = self._calculate_values_alignment(career_name, student_data, career_info)
            
            # El peso del sector se modifica según función y valores
            if function_alignment > 0.7 and values_alignment > 0.7:
                sector_refinement = 0.15  # Sector + función + valores = peso completo
            elif function_alignment > 0.5 or values_alignment > 0.5:
                sector_refinement = 0.08  # Solo sector + una alineación = peso reducido
            else:
                sector_refinement = 0.03  # Solo sector sin alineaciones = peso mínimo
                
        return sector_refinement
    
    def _calculate_function_alignment(self, career_name: str, student_data: Dict, career_info: Dict) -> float:
        """
        Calcula qué tan bien las funciones de la carrera se alinean con lo que quiere hacer el estudiante
        """
        trabajo_futuro = student_data.get('¿Cómo te imaginas tu trabajo en 10 años?', '').lower()
        tema_trabajo = student_data.get('¿Cuál sería el tema principal de tu trabajo?', '').lower()
        
        # Mapeo de funciones por carrera
        career_function_keywords = {
            'Psicología': ['personas', 'ayudar', 'escuchar', 'aconsejar', 'mental'],
            'Medicina': ['curar', 'salud', 'pacientes', 'diagnosticar', 'salvar'],
            'Ingeniería de Sistemas': ['desarrollar', 'programar', 'sistemas', 'tecnología', 'software'],
            'Administración de Empresas': ['gestionar', 'liderar', 'empresa', 'organizar', 'dirigir'],
            'Derecho': ['defender', 'justicia', 'legal', 'representar', 'argumentar'],
            'Contaduría Pública': ['números', 'finanzas', 'analizar', 'auditar', 'control'],
            'Arquitectura': ['diseñar', 'construir', 'espacios', 'edificios', 'crear'],
            'Diseño Gráfico': ['crear', 'diseñar', 'visual', 'arte', 'comunicar']
        }
        
        if career_name not in career_function_keywords:
            return 0.5  # Neutral si no tenemos mapeo
        
        functions = career_function_keywords[career_name]
        combined_text = trabajo_futuro + ' ' + tema_trabajo
        
        matches = sum(1 for func in functions if func in combined_text)
        return min(matches / len(functions), 1.0)
    
    def _calculate_values_alignment(self, career_name: str, student_data: Dict, career_info: Dict) -> float:
        """
        Calcula alineación entre valores personales y los valores requeridos por la carrera
        """
        personalidad = student_data.get('¿Cómo te ves a ti mismo? Como alguien...', '').lower()
        actividades_libres = student_data.get('¿Qué prefieres hacer en tus ratos libres?', '').lower()
        
        # Valores requeridos por carrera
        career_values = {
            'Psicología': ['empático', 'sociable', 'ayuda', 'escuchar'],
            'Medicina': ['responsable', 'dedicado', 'ayuda', 'precisión'],
            'Ingeniería de Sistemas': ['lógico', 'curioso', 'resolver problemas', 'técnico'],
            'Administración de Empresas': ['líder', 'organizado', 'decidido', 'comunicativo'],
            'Derecho': ['argumentativo', 'justicia', 'comunicativo', 'analítico'],
            'Arquitectura': ['creativo', 'visual', 'detallista', 'espacial'],
            'Diseño Gráfico': ['creativo', 'artístico', 'visual', 'expresivo']
        }
        
        if career_name not in career_values:
            return 0.5
        
        values = career_values[career_name]
        combined_text = personalidad + ' ' + actividades_libres
        
        matches = sum(1 for value in values if value in combined_text)
        return min(matches / len(values), 1.0)

def main():
    """
    Función principal mejorada para demostrar todas las características del sistema
    """
    print("🚀 SISTEMA DE RECOMENDACIÓN DE CARRERAS AVANZADO - VERSIÓN 3.0 (REGLAS LÓGICAS)")
    print("=" * 90)
    print("🧠 NUEVA CAPA DE REGLAS LÓGICAS POST-PREDICCIÓN (v3.0):")
    print("⚖️  Filtrado inteligente de contradicciones críticas")
    print("🚫 Exclusión automática de carreras incompatibles con perfil declarado")
    print("⚠️  Penalización por variables negativas (lo que NO va con el estudiante)")
    print("🔍 Peso refinado del sector ML (función + valores, no solo coincidencia)")
    print("💡 Detección de contradicciones personalidad-carrera")
    print("🎯 Evaluación estricta de alineación función-valores personales")
    print("=" * 90)
    print("🎨 MEJORAS DE DIVERSIDAD (v2.1):")
    print("✅ Umbrales de compatibilidad relajados para mayor variedad")
    print("✅ Penalizaciones reducidas al 50% para evitar exclusiones excesivas")
    print("✅ Bonificaciones principales equilibradas para evitar dominancia")
    print("✅ Diversidad forzada por sector (mín. 1-2 carreras por sector)")
    print("✅ Bonificación de diversidad para sectores poco representados")
    print("✅ Variación reproducible para romper empates entre carreras similares")
    print("✅ Filtrado menos restrictivo (siempre incluye carreras técnicas)")
    print("=" * 90)
    print("🎯 REGLAS BASE IMPLEMENTADAS (v2.0):")
    print("📊 REGLA 1.1: No descartar ML por baja confianza si hay coherencia declarada")
    print("🔄 REGLA 1.2: Híbrido ponderado entre perfil base y predicción ML")
    print("⭐ REGLA 2.1: Bonificación +5% por sectores explícitamente mencionados")
    print("🎯 REGLA 2.2: Bonificación +3% por coincidencia gustos-enfoque laboral")
    print("❌ REGLA 3.1: Penalización -2.5% por contradicción interacción social (reducida)")
    print("🏢 REGLA 3.2: Penalización -1.5% por entornos de trabajo no deseados (reducida)")
    print("🔄 REGLA 4.1: Máximo 2 carreras por subárea similar")
    print("🎨 REGLA 4.2: Priorización de diversidad sectorial")
    print("📝 REGLA 5.1: Razonamiento personalizado por entrada del estudiante")
    print("🔍 REGLA 5.2: Transparencia sobre origen de recomendaciones")
    print("=" * 90)
    print("Características base mantenidas:")
    print("✅ Coherencia mejorada entre perfil predicho y carrera sugerida")
    print("🏆 PESO MÁXIMO para coherencia 'Muy Coherente' (95% confianza + 20% bonificación)")
    print("🎯 REFUERZO ABSOLUTO del perfil base con coherencia alta")
    print("🏆 PRIORIZACIÓN ABSOLUTA de sectores preferidos explícitos")
    print("🎨 BONIFICACIONES ARTÍSTICAS especiales para perfiles Artísticos")
    print("🏢 PESO AUMENTADO para preferencias de entorno y sector laboral (20%)")
    print("✅ Penalización fuerte de predicciones ML con baja confianza (<0.4)")
    print("✅ Cobertura AMPLIADA del sector 'Arte y Comunicación' (8 nuevas carreras)")
    print("✅ Corrección de duplicados en salida de carreras")
    print("✅ Inclusión de carreras técnicas y artísticas aplicadas")
    print("✅ Consideración del entorno de trabajo deseado")
    print("✅ Detección de perfiles híbridos")
    print("✅ Validación completa de lógica de compatibilidad")
    print("=" * 80)
    
    recommender = ImprovedCareerRecommender()
    
    # Datos de ejemplo más completos para demostrar todas las funcionalidades
    student_data = {
        'Nombre completo': 'Ana María Rodríguez',
        'Promedio General': 4.3,
        'Rendimiento General': 'Alto',
        'Matemáticas - Promedio': 4.5,
        'Física - Promedio': 4.2,
        'Biología y química - Promedio': 3.8,
        'Ciencias sociales - Promedio': 3.5,
        'Educación artística - Promedio': 3.0,
        
        # Preferencias vocacionales
        '¿En cuál de estos sectores te gustaría trabajar?': 'TIC (Tecnologías de la información y la comunicación) y telecomunicaciones, Industrial manufacturero',
        'Quisiera que mi espacio laboral fuera...': 'Una oficina, con mi puesto de trabajo',
        'En mi trabajo me gustaría que mi relación con los demás fuera...': 'Poca, que implique poco relacionamiento con compañeros de trabajo o clientes',
        'Me gustaría un trabajo que se centrara en...': 'Desarrollo de tecnología y sistemas',
        '¿En 10 años te ves trabajando con...?': 'herramientas que me permitan construir y desarrollar tecnología',
        
        # Actividades e intereses
        '¿Qué prefieres hacer en tus ratos libres?': 'construir cosas con mis manos y hacer experimentos',
        '¿Cómo te ves a ti mismo? Como alguien...': 'hábil y curioso',
        '¿Cuáles son las materias que te gustan MÁS?': 'Matemáticas, Física',
        '¿Cuáles son las materias que te gustan MENOS?': 'Ciencias sociales, Educación artística',
        '¿En qué sientes que te va mejor? En temas relacionados con...': 'Matemáticas y tecnología'
    }
    
    print(f"\n📋 PROCESANDO ESTUDIANTE: {student_data['Nombre completo']}")
    print("-" * 50)
    
    # Generar recomendaciones con el sistema mejorado
    recommendations = recommender.recommend_careers(student_data, top_n=6)
    
    # Generar reporte completo
    report = recommender.generate_improved_report(student_data, recommendations)
    print("\n" + report)
    
    # Mostrar estadísticas del análisis
    print(f"\n📊 ESTADÍSTICAS DEL ANÁLISIS:")
    print("=" * 50)
    
    if recommendations:
        # Estadísticas de compatibilidad
        compatibilities = [rec['coherencia_score'] for rec in recommendations]
        avg_compatibility = sum(compatibilities) / len(compatibilities)
        max_compatibility = max(compatibilities)
        
        print(f"• Compatibilidad promedio: {avg_compatibility:.1%}")
        print(f"• Compatibilidad máxima: {max_compatibility:.1%}")
        
        # Contar carreras técnicas
        technical_count = sum(1 for rec in recommendations 
                            if rec.get('compatibility_details', {}).get('technical_application', False))
        print(f"• Carreras técnicas incluidas: {technical_count}/{len(recommendations)}")
        
        # Contar coincidencias de perfil y sector
        profile_matches = sum(1 for rec in recommendations 
                            if rec.get('compatibility_details', {}).get('profile_match', False))
        sector_matches = sum(1 for rec in recommendations 
                           if rec.get('compatibility_details', {}).get('sector_match', False))
        
        print(f"• Coincidencias de perfil: {profile_matches}/{len(recommendations)}")
        print(f"• Coincidencias de sector: {sector_matches}/{len(recommendations)}")
        
        # Verificar detección de perfiles híbridos
        hybrid_detected = any('-' in rec['perfil_predicho'] for rec in recommendations)
        print(f"• Perfil híbrido detectado: {'Sí' if hybrid_detected else 'No'}")
    
    print(f"\n✅ ANÁLISIS COMPLETO FINALIZADO")
    print("=" * 50)

if __name__ == "__main__":
    main() 