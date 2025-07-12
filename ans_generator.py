import json
import random
import pandas as pd
from faker import Faker

# Configurar Faker para español
fake = Faker('es_ES')

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
                # Usar materias favoritas del perfil
                if random.random() < 0.8 and profile['materias_favoritas']:
                    available = [opt for opt in profile['materias_favoritas'] if opt in question['options']]
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
            
            elif 'materias que te gustan MENOS' in question['question']:
                # Usar materias menos favoritas del perfil
                if random.random() < 0.8 and profile['materias_menos_favoritas']:
                    available = [opt for opt in profile['materias_menos_favoritas'] if opt in question['options']]
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
            
            elif 'materias te va MEJOR' in question['question']:
                # Usar materias buenas del perfil
                if random.random() < 0.8 and profile['materias_buenas']:
                    available = [opt for opt in profile['materias_buenas'] if opt in question['options']]
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
            
            elif 'NO TE VA BIEN' in question['question']:
                # Usar materias malas del perfil
                if random.random() < 0.8 and profile['materias_malas']:
                    available = [opt for opt in profile['materias_malas'] if opt in question['options']]
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
    
    # Guardar en CSV
    df_realistic.to_csv('generated_answers.csv', index=False, encoding='utf-8')
    print(f"Dataset generado con {len(df_realistic)} respuestas")
    print(f"Columnas: {len(df_realistic.columns)}")
    
    # Mostrar estadísticas básicas
    print("\nPrimeras 5 filas:")
    print(df_realistic.head())
    
    print("\nColumnas del dataset:")
    for col in df_realistic.columns:
        print(f"- {col}")
    
    # Mostrar algunos ejemplos de respuestas
    print("\nEjemplos de respuestas:")
    for i in range(3):
        print(f"\n--- Persona {i+1} ---")
        print(f"Nombre: {df_realistic.iloc[i]['Nombre completo']}")
        print(f"Ratos libres: {df_realistic.iloc[i]['¿Qué prefieres hacer en tus ratos libres?']}")
        print(f"Personalidad: {df_realistic.iloc[i]['¿Cómo te ves a ti mismo? Como alguien...']}")
        print(f"Materias favoritas: {df_realistic.iloc[i]['¿Cuáles son las materias que te gustan MÁS?']}")