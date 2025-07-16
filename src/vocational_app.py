"""
Aplicación de interfaz de usuario para el sistema de recomendación vocacional
"""

import pandas as pd
import sys
import os

# Añadir el directorio src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__)))

from career_recommender import CareerRecommender

class VocationalGuidanceApp:
    def __init__(self):
        self.recommender = CareerRecommender()
        self.dataset_path = '../data/dataset_completo.csv'
        
    def load_student_data(self):
        """Cargar datos completos del estudiante desde el CSV"""
        try:
            df = pd.read_csv(self.dataset_path)
            return df
        except FileNotFoundError:
            print("❌ Error: No se encontró el archivo dataset_completo.csv")
            return None
        except Exception as e:
            print(f"❌ Error al cargar los datos: {e}")
            return None
    
    def find_student(self, student_name, df):
        """Buscar estudiante por nombre en el dataset"""
        # Buscar coincidencias exactas primero
        exact_match = df[df['Nombre completo'].str.lower() == student_name.lower()]
        if not exact_match.empty:
            return exact_match.iloc[0]
        
        # Buscar coincidencias parciales
        partial_matches = df[df['Nombre completo'].str.lower().str.contains(student_name.lower(), na=False)]
        if not partial_matches.empty:
            if len(partial_matches) == 1:
                return partial_matches.iloc[0]
            else:
                print(f"\n🔍 Se encontraron múltiples estudiantes con '{student_name}':")
                for i, row in partial_matches.iterrows():
                    print(f"  - {row['Nombre completo']}")
                return None
        
        return None
    
    def display_available_students(self, df):
        """Mostrar lista de estudiantes disponibles"""
        print("\n📋 Estudiantes disponibles en el sistema:")
        print("=" * 50)
        for i, name in enumerate(df['Nombre completo'].tolist(), 1):
            print(f"{i:2d}. {name}")
        print("=" * 50)
    
    def prepare_student_data(self, student_row):
        """Preparar datos del estudiante para el sistema de recomendación"""
        # Usar los nombres de columna originales del dataset
        features = [
            # Numéricas
            'Física - Promedio', 'Biología y química - Promedio', 'Educación artística - Promedio',
            'Ciencias sociales - Promedio', 'Educación física - Promedio', 'Matemáticas - Promedio',
            'Lengua castellana - Promedio', 'Ciencias económicas y políticas - Promedio',
            'Promedio General', 'Cantidad Materias Favoritas', 'Cantidad Materias No Favoritas',
            'Cantidad Materias Buenas', 'Cantidad Materias Malas',
            # Categóricas
            'Rendimiento General', 'Física - Rendimiento', 'Biología y química - Rendimiento',
            'Educación artística - Rendimiento', 'Ciencias sociales - Rendimiento',
            'Educación física - Rendimiento', 'Matemáticas - Rendimiento',
            'Lengua castellana - Rendimiento', 'Ciencias económicas y políticas - Rendimiento',
            'Coherencia Gustos-Rendimiento',
            # Derivadas (pueden no estar presentes en el CSV, pero si están, se incluyen)
            'ratio_matematicas_ciencias', 'ratio_ciencias_sociales', 'std_notas', 'range_notas',
            'fortaleza_cientifica', 'fortaleza_humanistica', 'fortaleza_artistica',
            'balance_academico', 'coherencia_numerica', 'rendimiento_alto_count',
            'rendimiento_medio_count', 'rendimiento_bajo_count'
        ]
        academic_data = {}
        for feature in features:
            if feature in student_row:
                academic_data[feature] = student_row[feature]
        return academic_data
    
    def display_student_profile(self, student_row):
        """Mostrar perfil completo del estudiante"""
        name = student_row['Nombre completo']
        
        print(f"\n👤 PERFIL DEL ESTUDIANTE: {name}")
        print("=" * 60)
        
        # Información académica resumida
        print("\n📊 RENDIMIENTO ACADÉMICO:")
        print(f"  • Promedio General: {student_row.get('Promedio General', 'N/A')}")
        print(f"  • Rendimiento General: {student_row.get('Rendimiento General', 'N/A')}")
        
        # Materias favoritas y no favoritas
        print(f"\n📚 PREFERENCIAS ACADÉMICAS:")
        fav_subjects = student_row.get('¿Cuáles son las materias que te gustan MÁS?', 'N/A')
        least_subjects = student_row.get('¿Cuáles son las materias que te gustan MENOS?', 'N/A')
        print(f"  • Materias favoritas: {fav_subjects}")
        print(f"  • Materias menos favoritas: {least_subjects}")
        
        # Sector preferido y perfil
        print(f"\n🎯 PERFIL VOCACIONAL:")
        print(f"  • Perfil de Personalidad: {student_row.get('Perfil Personalidad', 'N/A')}")
        print(f"  • Sector Preferido: {student_row.get('Sector Preferido', 'N/A')}")
        print(f"  • Coherencia Gustos-Rendimiento: {student_row.get('Coherencia Gustos-Rendimiento', 'N/A')}")
        
        # Algunas respuestas vocacionales clave
        print(f"\n💼 PREFERENCIAS LABORALES:")
        work_sector = student_row.get('¿En cuál de estos sectores te gustaría trabajar?', 'N/A')
        work_focus = student_row.get('Me gustaría un trabajo que se centrara en...', 'N/A')
        print(f"  • Sector laboral preferido: {work_sector}")
        print(f"  • Enfoque de trabajo: {work_focus}")
        
        print("=" * 60)
    
    def run(self):
        """Ejecutar la aplicación principal"""
        print("🎓 SISTEMA DE ORIENTACIÓN VOCACIONAL")
        print("=" * 50)
        print("Este sistema analiza tu perfil académico y vocacional")
        print("para recomendarte carreras universitarias apropiadas.")
        print("=" * 50)
        
        # Cargar datos
        df = self.load_student_data()
        if df is None:
            return
        
        while True:
            print(f"\n📝 Ingresa el nombre del estudiante:")
            print("(Puedes escribir el nombre completo o solo parte del nombre)")
            
            student_name = input("👤 Nombre: ").strip()
            
            if not student_name:
                print("❌ Por favor ingresa un nombre válido")
                continue
            
            # Buscar estudiante
            student_data = self.find_student(student_name, df)
            
            if student_data is None:
                print(f"\n❌ No se encontró el estudiante '{student_name}'")
                
                response = input("\n¿Deseas ver la lista de estudiantes disponibles? (s/n): ").strip().lower()
                if response == 's':
                    self.display_available_students(df)
                
                continue_search = input("\n¿Deseas buscar otro estudiante? (s/n): ").strip().lower()
                if continue_search != 's':
                    break
                continue
            
            # Mostrar perfil del estudiante
            self.display_student_profile(student_data)
            
            # Preparar datos para recomendación
            academic_data = self.prepare_student_data(student_data)
            
            # Generar recomendaciones
            print(f"\n🔄 Generando recomendaciones para {student_data['Nombre completo']}...")
            recommendations = self.recommender.recommend_careers(academic_data)
            
            if recommendations:
                print(f"\n🎯 RECOMENDACIONES DE CARRERAS UNIVERSITARIAS")
                print("=" * 60)
                
                # Mostrar perfil predicho
                if recommendations:
                    print(f"\n🧠 Perfil de personalidad predicho: {recommendations[0]['perfil_predicho']}")
                    print(f"🏢 Sector laboral predicho: {recommendations[0]['sector_predicho']}")
                    print("=" * 60)
                
                for i, rec in enumerate(recommendations, 1):
                    print(f"\n{i}. {rec['nombre']}")
                    print(f"   📊 Compatibilidad: {rec['puntuacion']:.1%}")
                    print(f"   📝 Descripción: {rec['descripcion']}")
                    print(f"   🏛️  Universidades: {', '.join(rec['universidades'])}")
                    print(f"   ⏱️  Duración: {rec['duracion']}")
                    print(f"   💰 Salario promedio: {rec['salario_promedio']}")
                    
                    # Mostrar razones de la recomendación
                    matches = []
                    if rec['match_perfil']:
                        matches.append(f"✅ Coincide con tu perfil ({rec['perfil_predicho']})")
                    if rec['match_sector']:
                        matches.append(f"✅ Coincide con tu sector preferido ({rec['sector_predicho']})")
                    
                    if matches:
                        print(f"   🎯 Razones de recomendación:")
                        for match in matches:
                            print(f"     {match}")
                    
                    if i >= 5:  # Mostrar solo las top 5
                        break
            else:
                print("\n❌ No se pudieron generar recomendaciones")
            
            # Preguntar si desea consultar otro estudiante
            print("\n" + "=" * 60)
            another_student = input("¿Deseas consultar otro estudiante? (s/n): ").strip().lower()
            if another_student != 's':
                break
        
        print("\n👋 ¡Gracias por usar el Sistema de Orientación Vocacional!")

if __name__ == "__main__":
    app = VocationalGuidanceApp()
    app.run() 