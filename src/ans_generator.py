import json
import random
import pandas as pd
from faker import Faker

# Configurar Faker para español
fake = Faker('es_ES')

def generate_grades_for_subject(subject, is_favorite, is_good_at, target_passing=True):
    """Genera 4 notas trimestrales para una materia basándose en si es favorita y si le va bien"""
    
    if target_passing:
        # Si queremos que apruebe la materia (promedio ≥ 3.0)
        if is_favorite and is_good_at:
            # Si le gusta Y le va bien: notas altas (3.5-5.0) - garantiza aprobar
            base_grade = random.uniform(3.5, 5.0)
        elif is_favorite and not is_good_at:
            # Si le gusta pero no le va bien: notas medias-altas (3.0-4.0) - puede aprobar
            base_grade = random.uniform(3.0, 4.0)
        elif not is_favorite and is_good_at:
            # Si no le gusta pero le va bien: notas medias (3.0-3.8) - puede aprobar
            base_grade = random.uniform(3.0, 3.8)
        else:
            # Si no le gusta Y no le va bien: notas bajas pero aprobatorias (3.0-3.5)
            base_grade = random.uniform(3.0, 3.5)
    else:
        # Si queremos que repruebe la materia (promedio < 3.0)
        if is_favorite and is_good_at:
            # Si le gusta Y le va bien pero queremos que repruebe: notas bajas (2.0-2.9)
            base_grade = random.uniform(2.0, 2.9)
        elif is_favorite and not is_good_at:
            # Si le gusta pero no le va bien: notas bajas (1.5-2.8)
            base_grade = random.uniform(1.5, 2.8)
        elif not is_favorite and is_good_at:
            # Si no le gusta pero le va bien: notas bajas (2.0-2.9)
            base_grade = random.uniform(2.0, 2.9)
        else:
            # Si no le gusta Y no le va bien: notas muy bajas (1.0-2.5)
            base_grade = random.uniform(1.0, 2.5)
    
    # Generar 4 notas con variación pequeña (±0.3 puntos)
    grades = []
    for i in range(4):
        variation = random.uniform(-0.3, 0.3)
        grade = max(1.0, min(5.0, base_grade + variation))  # Limitar entre 1.0 y 5.0
        grades.append(round(grade, 1))
    
    return grades

def generate_response(question):
    """Genera una respuesta simulada basada en el tipo de pregunta"""
    
    if question['type'] == 'text':
        # Para el nombre completo
        if question.get('faker_provider') == 'name':
            return fake.name()
        else:
            return fake.text(max_nb_chars=100)
    
    elif question['type'] == 'multiple_choice':
        # Seleccionar una opción
        return random.choice(question['options'])
    
    elif question['type'] == 'checkbox':
        # Seleccionar entre 1 y max_selections opciones
        max_sel = question.get('max_selections', len(question['options']))
        num_selections = random.randint(1, min(max_sel, len(question['options'])))
        selected = random.sample(question['options'], num_selections)
        return selected

def generate_realistic_responses(form_structure, num_responses=100):
    """Genera respuestas más realistas considerando coherencia entre preguntas"""
    
    dataset = []
    
    # Definir perfiles más específicos
    profiles = {
        'artistico': {
            'materias_favoritas': ['Educación artística', 'Lengua castellana'],
            'materias_menos_favoritas': ['Matemáticas', 'Física'],
            'materias_buenas': ['Educación artística', 'Lengua castellana'],
            'materias_malas': ['Matemáticas', 'Física', 'Biología y química'],
            'actividades_libres': ['Hacer actividades artisticas'],
            'personalidad': ['Imaginativo. Me expreso creativamente'],
            'trabajo_futuro': ['Creaciones propias relacionadas con el arte'],
            'sector_preferido': ['Cultural y artístico', 'Educación'],
            'tema_trabajo': ['El diseño, música, baile, teatro y cocina'],
            'habilidades': ['La creación y representación de objetos e imágenes']
        },
        'cientifico': {
            'materias_favoritas': ['Física', 'Biología y química', 'Matemáticas'],
            'materias_menos_favoritas': ['Educación artística', 'Educación física'],
            'materias_buenas': ['Física', 'Biología y química', 'Matemáticas'],
            'materias_malas': ['Educación artística', 'Educación física'],
            'actividades_libres': ['Leer o hacer experimentos'],
            'personalidad': ['Curioso. Me gusta entender el porqué de las cosas'],
            'trabajo_futuro': ['Información y datos, para clasificar y analizar'],
            'sector_preferido': ['Investigación en ciencias básicas y aplicadas', 'Salud'],
            'tema_trabajo': ['La naturaleza, el universo y su funcionamiento'],
            'habilidades': ['Las matemáticas: el cálculo, los símbolos y la lógica']
        },
        'social': {
            'materias_favoritas': ['Ciencias sociales', 'Lengua castellana'],
            'materias_menos_favoritas': ['Matemáticas', 'Física'],
            'materias_buenas': ['Ciencias sociales', 'Lengua castellana', 'Ciencias económicas y políticas'],
            'materias_malas': ['Matemáticas', 'Física'],
            'actividades_libres': ['Escuchar y conversas con mis amigos'],
            'personalidad': ['Sociable. Disfruto compartir con otros'],
            'trabajo_futuro': ['Personas, enseñando o cuidando de ellas'],
            'sector_preferido': ['Educación', 'Desarrollo humano y social'],
            'tema_trabajo': ['El aprendizaje de niños, jóvenes y adultos'],
            'habilidades': ['Las personas, el relacionamiento y comunicación con otros']
        },
        'tecnico': {
            'materias_favoritas': ['Matemáticas', 'Física'],
            'materias_menos_favoritas': ['Ciencias sociales', 'Lengua castellana'],
            'materias_buenas': ['Matemáticas', 'Física'],
            'materias_malas': ['Ciencias sociales', 'Lengua castellana', 'Educación artística'],
            'actividades_libres': ['Practicar deporte o construir cosas'],
            'personalidad': ['Hábil. Soy bueno para el trabajo manual'],
            'trabajo_futuro': ['Herramientas que me permitan construir y crear'],
            'sector_preferido': ['Industrial manufacturero', 'Construcción', 'TIC (Tecnologías de la información y la comunicación) y telecomunicaciones'],
            'tema_trabajo': ['El desarrollo y el funcionamiento de objetos'],
            'habilidades': ['Las matemáticas: el cálculo, los símbolos y la lógica']
        }
    }
    
    for i in range(num_responses):
        response = {}
        
        # Seleccionar un perfil aleatorio
        profile_name = random.choice(list(profiles.keys()))
        profile = profiles[profile_name]
        
        # Variables para mantener coherencia entre respuestas de materias
        materias_que_van_bien = []
        materias_que_van_mal = []
        materias_que_gustan_mas = []
        materias_que_gustan_menos = []
        
        # Lista de todas las materias disponibles
        todas_las_materias = [
            "Física", "Biología y química", "Educación artística", "Ciencias sociales",
            "Educación física", "Matemáticas", "Lengua castellana", "Ciencias económicas y políticas"
        ]
        
        for question in form_structure['questions']:
            answer = None
            
            # Generar respuestas basadas en el perfil
            if 'Nombre completo' in question['question']:
                answer = fake.name()
            
            elif 'ratos libres' in question['question']:
                # Usar actividades del perfil con probabilidad alta
                if random.random() < 0.7 and profile['actividades_libres']:
                    selected = profile['actividades_libres'][:]
                    # Agregar una actividad aleatoria más
                    remaining = [opt for opt in question['options'] if opt not in selected]
                    if remaining:
                        selected.append(random.choice(remaining))
                    answer = selected[:question.get('max_selections', 2)]
                else:
                    answer = generate_response(question)
            
            elif 'Cómo te ves' in question['question']:
                # Usar personalidad del perfil
                if random.random() < 0.8 and profile['personalidad']:
                    selected = profile['personalidad'][:]
                    remaining = [opt for opt in question['options'] if opt not in selected]
                    if remaining and len(selected) < question.get('max_selections', 2):
                        selected.append(random.choice(remaining))
                    answer = selected[:question.get('max_selections', 2)]
                else:
                    answer = generate_response(question)
            
            elif '10 años' in question['question']:
                # Usar trabajo futuro del perfil
                if random.random() < 0.8 and profile['trabajo_futuro']:
                    selected = profile['trabajo_futuro'][:]
                    remaining = [opt for opt in question['options'] if opt not in selected]
                    if remaining and len(selected) < question.get('max_selections', 2):
                        selected.append(random.choice(remaining))
                    answer = selected[:question.get('max_selections', 2)]
                else:
                    answer = generate_response(question)
            
            elif 'materias que te gustan MÁS' in question['question']:
                # Usar materias favoritas del perfil pero EXCLUYENDO las que ya dijo que le gustan menos
                if random.random() < 0.8 and profile['materias_favoritas']:
                    # Filtrar materias que NO están en las que gustan menos
                    available = [opt for opt in profile['materias_favoritas'] 
                               if opt in question['options'] and opt not in materias_que_gustan_menos]
                    if available:
                        selected = available[:]
                        remaining = [opt for opt in question['options'] 
                                   if opt not in selected and opt not in materias_que_gustan_menos]
                        while len(selected) < question.get('max_selections', 3) and remaining:
                            selected.append(random.choice(remaining))
                            remaining.remove(selected[-1])
                        answer = selected[:question.get('max_selections', 3)]
                        materias_que_gustan_mas = answer[:]
                    else:
                        # Si no hay materias del perfil disponibles, usar cualquier materia que no esté en las que gustan menos
                        remaining = [opt for opt in question['options'] if opt not in materias_que_gustan_menos]
                        if remaining:
                            num_selections = min(question.get('max_selections', 3), len(remaining))
                            answer = random.sample(remaining, num_selections)
                            materias_que_gustan_mas = answer[:]
                        else:
                            answer = []
                            materias_que_gustan_mas = []
                else:
                    # Generar respuesta aleatoria pero excluyendo las que gustan menos
                    remaining = [opt for opt in question['options'] if opt not in materias_que_gustan_menos]
                    if remaining:
                        num_selections = min(question.get('max_selections', 3), len(remaining))
                        answer = random.sample(remaining, num_selections)
                        materias_que_gustan_mas = answer[:]
                    else:
                        answer = []
                        materias_que_gustan_mas = []
            
            elif 'materias que te gustan MENOS' in question['question']:
                # Usar materias menos favoritas del perfil pero EXCLUYENDO las que ya dijo que le gustan más
                if random.random() < 0.8 and profile['materias_menos_favoritas']:
                    # Filtrar materias que NO están en las que gustan más
                    available = [opt for opt in profile['materias_menos_favoritas'] 
                               if opt in question['options'] and opt not in materias_que_gustan_mas]
                    if available:
                        selected = available[:]
                        remaining = [opt for opt in question['options'] 
                                   if opt not in selected and opt not in materias_que_gustan_mas]
                        while len(selected) < question.get('max_selections', 3) and remaining:
                            selected.append(random.choice(remaining))
                            remaining.remove(selected[-1])
                        answer = selected[:question.get('max_selections', 3)]
                        materias_que_gustan_menos = answer[:]
                    else:
                        # Si no hay materias del perfil disponibles, usar cualquier materia que no esté en las que gustan más
                        remaining = [opt for opt in question['options'] if opt not in materias_que_gustan_mas]
                        if remaining:
                            num_selections = min(question.get('max_selections', 3), len(remaining))
                            answer = random.sample(remaining, num_selections)
                            materias_que_gustan_menos = answer[:]
                        else:
                            answer = []
                            materias_que_gustan_menos = []
                else:
                    # Generar respuesta aleatoria pero excluyendo las que gustan más
                    remaining = [opt for opt in question['options'] if opt not in materias_que_gustan_mas]
                    if remaining:
                        num_selections = min(question.get('max_selections', 3), len(remaining))
                        answer = random.sample(remaining, num_selections)
                        materias_que_gustan_menos = answer[:]
                    else:
                        answer = []
                        materias_que_gustan_menos = []
            
            elif 'materias te va MEJOR' in question['question']:
                # Usar materias buenas del perfil y guardar para coherencia
                if random.random() < 0.8 and profile['materias_buenas']:
                    available = [opt for opt in profile['materias_buenas'] if opt in question['options']]
                    if available:
                        selected = available[:]
                        remaining = [opt for opt in question['options'] if opt not in selected]
                        while len(selected) < question.get('max_selections', 3) and remaining:
                            selected.append(random.choice(remaining))
                            remaining.remove(selected[-1])
                        answer = selected[:question.get('max_selections', 3)]
                        materias_que_van_bien = answer[:]
                    else:
                        answer = generate_response(question)
                        materias_que_van_bien = answer[:] if isinstance(answer, list) else [answer]
                else:
                    answer = generate_response(question)
                    materias_que_van_bien = answer[:] if isinstance(answer, list) else [answer]
            
            elif 'NO TE VA BIEN' in question['question']:
                # Usar materias malas del perfil pero EXCLUYENDO las que ya dijo que le van bien
                if random.random() < 0.8 and profile['materias_malas']:
                    # Filtrar materias que NO están en las que van bien
                    available = [opt for opt in profile['materias_malas'] 
                               if opt in question['options'] and opt not in materias_que_van_bien]
                    if available:
                        selected = available[:]
                        remaining = [opt for opt in question['options'] 
                                   if opt not in selected and opt not in materias_que_van_bien]
                        while len(selected) < question.get('max_selections', 3) and remaining:
                            selected.append(random.choice(remaining))
                            remaining.remove(selected[-1])
                        answer = selected[:question.get('max_selections', 3)]
                        materias_que_van_mal = answer[:]
                    else:
                        # Si no hay materias del perfil disponibles, usar cualquier materia que no esté en las que van bien
                        remaining = [opt for opt in question['options'] if opt not in materias_que_van_bien]
                        if remaining:
                            num_selections = min(question.get('max_selections', 3), len(remaining))
                            answer = random.sample(remaining, num_selections)
                            materias_que_van_mal = answer[:]
                        else:
                            answer = []
                            materias_que_van_mal = []
                else:
                    # Generar respuesta aleatoria pero excluyendo las que van bien
                    remaining = [opt for opt in question['options'] if opt not in materias_que_van_bien]
                    if remaining:
                        num_selections = min(question.get('max_selections', 3), len(remaining))
                        answer = random.sample(remaining, num_selections)
                        materias_que_van_mal = answer[:]
                    else:
                        answer = []
                        materias_que_van_mal = []
            
            elif 'sectores te gustaría trabajar' in question['question']:
                # Usar sectores del perfil
                if random.random() < 0.7 and profile['sector_preferido']:
                    available = [opt for opt in profile['sector_preferido'] if opt in question['options']]
                    if available:
                        selected = available[:]
                        remaining = [opt for opt in question['options'] if opt not in selected]
                        while len(selected) < question.get('max_selections', 3) and remaining:
                            selected.append(random.choice(remaining))
                            remaining.remove(selected[-1])
                        answer = selected[:question.get('max_selections', 3)]
                    else:
                        answer = generate_response(question)
                else:
                    answer = generate_response(question)
            
            elif 'tema principal de tu trabajo' in question['question']:
                # Usar tema de trabajo del perfil
                if random.random() < 0.7 and profile['tema_trabajo']:
                    available = [opt for opt in profile['tema_trabajo'] if opt in question['options']]
                    if available:
                        selected = available[:]
                        remaining = [opt for opt in question['options'] if opt not in selected]
                        while len(selected) < question.get('max_selections', 3) and remaining:
                            selected.append(random.choice(remaining))
                            remaining.remove(selected[-1])
                        answer = selected[:question.get('max_selections', 3)]
                    else:
                        answer = generate_response(question)
                else:
                    answer = generate_response(question)
            
            elif 'sientes que te va mejor' in question['question']:
                # Usar habilidades del perfil
                if random.random() < 0.7 and profile['habilidades']:
                    available = [opt for opt in profile['habilidades'] if opt in question['options']]
                    if available:
                        selected = available[:]
                        remaining = [opt for opt in question['options'] if opt not in selected]
                        while len(selected) < question.get('max_selections', 2) and remaining:
                            selected.append(random.choice(remaining))
                            remaining.remove(selected[-1])
                        answer = selected[:question.get('max_selections', 2)]
                    else:
                        answer = generate_response(question)
                else:
                    answer = generate_response(question)
            
            else:
                # Para otras preguntas, generar respuesta normal
                answer = generate_response(question)
            
            # Guardar la respuesta en el formato correcto
            if question['type'] == 'checkbox':
                if isinstance(answer, list):
                    # Convertir a string separado por comas para mejor legibilidad
                    response[question['question']] = ', '.join(answer)
                else:
                    response[question['question']] = answer
            else:
                response[question['question']] = answer
        
        # Determinar cuántas materias debe reprobar el estudiante (realista)
        # 70% aprueba todo, 20% reprueba 1-2 materias, 10% reprueba 3+ materias
        reprobation_chance = random.random()
        if reprobation_chance < 0.7:
            materias_a_reprobar = 0  # Aprueba todo
        elif reprobation_chance < 0.9:
            materias_a_reprobar = random.randint(1, 2)  # Reprueba 1-2 materias
        else:
            materias_a_reprobar = random.randint(3, 4)  # Reprueba 3-4 materias
        
        # Determinar qué materias reprobará (priorizar las que no le gustan/no le van bien)
        materias_para_reprobar = []
        if materias_a_reprobar > 0:
            # Crear lista de materias ordenadas por probabilidad de reprobar
            materias_por_probabilidad = []
            
            for materia in todas_las_materias:
                is_favorite = materia in materias_que_gustan_mas
                is_good_at = materia in materias_que_van_bien
                
                # Calcular probabilidad de reprobar (más alta si no le gusta Y no le va bien)
                if not is_favorite and not is_good_at:
                    prob = 0.8
                elif not is_favorite or not is_good_at:
                    prob = 0.5
                else:
                    prob = 0.2
                
                materias_por_probabilidad.append((materia, prob))
            
            # Ordenar por probabilidad (más alta primero)
            materias_por_probabilidad.sort(key=lambda x: x[1], reverse=True)
            
            # Seleccionar las materias a reprobar
            materias_para_reprobar = [m[0] for m in materias_por_probabilidad[:materias_a_reprobar]]
        
        # Generar notas trimestrales para cada materia
        for materia in todas_las_materias:
            # Determinar si la materia es favorita y si le va bien
            is_favorite = materia in materias_que_gustan_mas
            is_good_at = materia in materias_que_van_bien
            
            # Determinar si debe aprobar o reprobar esta materia
            debe_aprobar = materia not in materias_para_reprobar
            
            # Generar las 4 notas trimestrales
            notas = generate_grades_for_subject(materia, is_favorite, is_good_at, debe_aprobar)
            
            # Añadir las notas al response con nombres de columnas descriptivos
            response[f'{materia} - Trimestre 1'] = notas[0]
            response[f'{materia} - Trimestre 2'] = notas[1]
            response[f'{materia} - Trimestre 3'] = notas[2]
            response[f'{materia} - Trimestre 4'] = notas[3]
        
        dataset.append(response)
    
    return pd.DataFrame(dataset)

# Ejemplo de uso
if __name__ == "__main__":
    # Cargar la estructura del formulario
    with open('form_structure.json', 'r', encoding='utf-8') as f:
        form_structure = json.load(f)
    
    # Generar dataset realista
    print("Generando respuestas simuladas...")
    df_realistic = generate_realistic_responses(form_structure, num_responses=5)
    
    # Separar los datos en dos DataFrames
    # 1. Datos del formulario (preferencias y aspiraciones)
    form_columns = [col for col in df_realistic.columns if 'Trimestre' not in col]
    df_formulario = df_realistic[form_columns].copy()
    
    # 2. Datos académicos (notas trimestrales)
    grades_columns = [col for col in df_realistic.columns if 'Trimestre' in col]
    # Añadir el nombre del estudiante para poder relacionar los datos
    grades_columns.insert(0, 'Nombre completo')
    df_notas = df_realistic[grades_columns].copy()
    
    # Guardar en CSV separados en el directorio data
    df_formulario.to_csv('../data/respuestas_formulario.csv', index=False, encoding='utf-8')
    df_notas.to_csv('../data/notas_academicas.csv', index=False, encoding='utf-8')
    
    print(f"Dataset generado con {len(df_realistic)} respuestas")
    print(f"Columnas del formulario: {len(df_formulario.columns)}")
    print(f"Columnas de notas: {len(df_notas.columns)}")
    
    # Mostrar estadísticas básicas
    print("\nPrimeras 5 filas del formulario:")
    print(df_formulario.head())
    
    print("\nPrimeras 5 filas de notas:")
    print(df_notas.head())
    
    print("\nColumnas del formulario:")
    for col in df_formulario.columns:
        print(f"- {col}")
    
    print("\nColumnas de notas:")
    for col in df_notas.columns:
        print(f"- {col}")
    
    # Mostrar algunos ejemplos de respuestas
    print("\nEjemplos de respuestas:")
    for i in range(3):
        print(f"\n--- Persona {i+1} ---")
        print(f"Nombre: {df_formulario.iloc[i]['Nombre completo']}")
        print(f"Ratos libres: {df_formulario.iloc[i]['¿Qué prefieres hacer en tus ratos libres?']}")
        print(f"Personalidad: {df_formulario.iloc[i]['¿Cómo te ves a ti mismo? Como alguien...']}")
        print(f"Materias favoritas: {df_formulario.iloc[i]['¿Cuáles son las materias que te gustan MÁS?']}")
        
        # Mostrar algunas notas como ejemplo
        print("Notas de Matemáticas:")
        for j in range(1, 5):
            col_name = f"Matemáticas - Trimestre {j}"
            if col_name in df_notas.columns:
                print(f"  Trimestre {j}: {df_notas.iloc[i][col_name]}")