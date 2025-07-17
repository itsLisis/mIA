# 🎓 Sistema de Recomendación Vocacional - mIA

## ¿Qué es este proyecto?

**mIA** es un sistema inteligente que ayuda a estudiantes a descubrir qué carrera universitaria se adapta mejor a su perfil personal. Funciona como un consejero vocacional digital que analiza las notas académicas, intereses y preferencias personales del estudiante para sugerir las carreras más compatibles.

## ¿Cómo funciona?

El sistema es muy simple de usar:

1. **Ingresa el nombre del estudiante** que quiere recibir recomendaciones
2. **El sistema analiza automáticamente** sus notas y respuestas de orientación vocacional
3. **Recibe hasta 8 recomendaciones personalizadas** de carreras universitarias
4. **Cada recomendación incluye**:
   - Porcentaje de compatibilidad con el estudiante
   - Descripción de la carrera
   - Universidades donde se puede estudiar
   - Duración y rango salarial promedio
   - Razones específicas por las que se recomienda

## ¿Qué información utiliza?

El sistema analiza múltiples aspectos del perfil estudiantil:

- **Rendimiento académico**: Notas en materias como matemáticas, ciencias, artes, etc.
- **Intereses personales**: Qué le gusta hacer en su tiempo libre
- **Preferencias laborales**: Tipo de trabajo que le gustaría tener
- **Personalidad**: Cómo se ve a sí mismo y sus fortalezas
- **Sectores de interés**: Áreas donde le gustaría trabajar (tecnología, salud, educación, etc.)

## Características principales

**Recomendaciones personalizadas** basadas en el perfil único de cada estudiante  
 **Base de datos completa** con 156 carreras universitarias colombianas  
 **Análisis inteligente** que detecta contradicciones y filtra opciones incoherentes  
 **Explicaciones claras** de por qué se recomienda cada carrera  
 **Información práctica** sobre universidades, duración y salarios  
 **Diversidad en recomendaciones** para mostrar diferentes opciones

## ¿Para quién es útil?

- **Estudiantes de último año** que necesitan elegir carrera universitaria
- **Orientadores educativos** que quieren herramientas adicionales de apoyo
- **Padres de familia** que buscan ayudar a sus hijos en la decisión vocacional
- **Instituciones educativas** interesadas en sistemas de orientación vocacional

## Estructura del proyecto

```
mIA/
├── data/                    # Base de datos de estudiantes y carreras
│   ├── dataset_completo_clean.csv
│   ├── careers_database.json
│   └── respuestas_formulario.csv
├── src/                     # Código del sistema
│   ├── vocational_app.py           # Aplicación principal
│   ├── improved_career_recommender.py  # Motor de recomendaciones
│   ├── career_database.py          # Base de datos de carreras
│   └── ans_generator.py            # Generador de datos de prueba
├── models/                  # Modelos de inteligencia artificial
└── myEnv/                   # Entorno virtual de Python
```

## ¿Cómo usar el sistema?

### Paso 1: Preparación

```bash
# Activar el entorno virtual
.\myEnv\Scripts\Activate.ps1

# Ir a la carpeta del código
cd src
```

### Paso 2: Ejecutar el sistema

```bash
# Iniciar la aplicación
python vocational_app.py
```

### Paso 3: Seguir las instrucciones

- El sistema te pedirá el nombre completo del estudiante
- Buscará automáticamente sus datos en la base de datos
- Mostrará las recomendaciones de carreras más compatibles

## Ejemplo de recomendación

```
1. Ingeniería de Sistemas
    Compatibilidad: 89.2%
    Descripción: Desarrollo de software y sistemas tecnológicos
    Universidades: Universidad Nacional, Universidad de los Andes, EAFIT
    Duración: 5 años
    Salario promedio: 3.500.000 - 8.000.000 COP
    Razones:
      Excelente rendimiento en matemáticas
      Interés declarado en tecnología
      Perfil técnico compatible
      Sector TIC es tu preferencia principal
```

## Tecnología utilizada

El sistema funciona con **Python** y utiliza técnicas de **inteligencia artificial** para hacer las recomendaciones, pero no necesitas saber programación para usarlo. Todo está automatizado y funciona a través de una interfaz simple de consola.

## Requisitos del sistema

- **Python 3.9+** instalado en el computador
- **Windows, Mac o Linux** (el sistema es compatible con todos)
- **5 minutos** para la instalación inicial
- **Conexión a internet** no requerida después de la instalación

## Instalación

```bash
# Clonar o descargar el proyecto
git clone [URL_del_proyecto]

# Instalar dependencias
pip install -r requirements.txt
```

## ¿Qué hace diferente a este sistema?

A diferencia de tests vocacionales tradicionales, este sistema:

- **No solo pregunta qué te gusta**, sino que analiza tu rendimiento real
- **Detecta contradicciones** entre lo que dices y lo que demuestran tus notas
- **Considera múltiples factores** al mismo tiempo para dar recomendaciones más precisas
- **Explica sus decisiones** de manera clara y personalizada
- **Se adapta a cada estudiante** en lugar de usar fórmulas genéricas

## Apoyo y contacto

Este sistema fue desarrollado como proyecto académico para ayudar en la orientación vocacional de estudiantes colombianos. Si tienes preguntas o sugerencias, no dudes en contactarnos.

---

_Desarrollado con amor para ayudar a estudiantes a encontrar su camino profesional_
