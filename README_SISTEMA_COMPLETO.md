# 🎓 Sistema de Recomendación Vocacional

Un sistema completo de inteligencia artificial para recomendar carreras universitarias basado en el perfil académico y vocacional de los estudiantes.

## 📋 Características

- **Análisis de Perfil Vocacional**: Predice el perfil de personalidad del estudiante
- **Predicción de Sector Laboral**: Identifica el sector laboral preferido
- **Recomendaciones Personalizadas**: Sugiere carreras específicas basadas en predicciones
- **Base de Datos Completa**: 16+ carreras universitarias reales con información detallada
- **Interfaz Amigable**: Aplicación de consola interactiva
- **Reportes Detallados**: Genera reportes guardables con recomendaciones

## 🚀 Instalación

1. **Clonar el repositorio**:

   ```bash
   git clone <repository-url>
   cd mIA
   ```

2. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Entrenar los modelos** (primera vez):
   ```bash
   python src/train_model.py
   ```

## 📁 Estructura del Proyecto

```
mIA/
├── data/
│   ├── dataset_completo.csv          # Datos procesados de estudiantes
│   ├── careers_database.json         # Base de datos de carreras
│   └── ...
├── models/
│   ├── vocacional_model_perfil_personalidad.pkl
│   └── vocacional_model_sector_preferido.pkl
├── src/
│   ├── train_model.py               # Entrenamiento de modelos ML
│   ├── career_database.py           # Base de datos de carreras
│   ├── career_recommender.py        # Sistema de recomendación
│   ├── vocational_app.py           # Interfaz de usuario
│   └── analyze_data.py             # Análisis de datos
├── reports/                         # Reportes generados
└── requirements.txt
```

## 🎯 Cómo Usar el Sistema

### 1. Entrenamiento de Modelos (Solo primera vez)

```bash
python src/train_model.py
```

Este comando:

- Entrena modelos RandomForest para predecir perfil de personalidad y sector preferido
- Evalúa el rendimiento de los modelos
- Guarda los modelos entrenados en la carpeta `models/`

### 2. Análisis de Datos

```bash
python src/analyze_data.py
```

Muestra estadísticas del dataset y distribución de perfiles vocacionales.

### 3. Usar la Aplicación Principal

```bash
python src/vocational_app.py
```

La aplicación te guiará a través de:

1. **Ingreso de datos**: Nombre, promedios académicos, rendimiento general
2. **Análisis**: El sistema predice tu perfil vocacional
3. **Recomendaciones**: Muestra las 5 carreras más compatibles
4. **Reporte**: Opción de guardar reporte detallado

## 🧠 Modelos de Machine Learning

### Perfiles de Personalidad Vocacional

- **Investigador**: Curioso, analítico, le gusta la investigación
- **Técnico**: Hábil, práctico, bueno para trabajo manual
- **Artístico**: Imaginativo, creativo, expresivo
- **Organizador**: Organizado, sistemático, estructurado
- **Líder**: Iniciativa, toma decisiones, dirige equipos
- **Social**: Sociable, empático, le gusta ayudar

### Sectores Laborales

- **Educativo**: Enseñanza, formación, desarrollo humano
- **Salud**: Medicina, enfermería, bienestar
- **Tecnología**: TIC, desarrollo, innovación
- **Industrial**: Manufactura, construcción, ingeniería
- **Cultural**: Arte, diseño, entretenimiento
- **Investigación**: Ciencia, desarrollo, análisis
- **Otros**: Derecho, administración, servicios

## 📚 Carreras Incluidas

### Ingeniería y Tecnología

- Ingeniería de Sistemas
- Ingeniería Civil
- Ingeniería Biomédica
- Ingeniería de Software
- Diseño Industrial

### Salud

- Medicina
- Enfermería
- Psicología

### Educación

- Licenciatura en Matemáticas
- Licenciatura en Educación Física

### Arte y Cultura

- Diseño Gráfico
- Música

### Ciencias Sociales

- Derecho
- Administración de Empresas

### Ciencias Naturales

- Biología
- Química

## 🔧 Uso Avanzado

### Probar el Sistema de Recomendación

```bash
python src/career_recommender.py
```

### Crear/Actualizar Base de Datos de Carreras

```bash
python src/career_database.py
```

## 📊 Métricas del Modelo

El sistema usa RandomForestClassifier con las siguientes características:

- **Features**: 23 variables (promedios académicos, rendimiento, coherencia)
- **Precisión típica**: 70-85% dependiendo del perfil
- **Validación**: División 80/20 entrenamiento/prueba

## 🎨 Ejemplo de Uso

```python
from src.career_recommender import CareerRecommender

# Crear instancia del recomendador
recommender = CareerRecommender()

# Datos del estudiante
student_data = {
    'Nombre completo': 'Juan Pérez',
    'Matemáticas - Promedio': 4.5,
    'Física - Promedio': 4.2,
    'Promedio General': 3.8,
    'Rendimiento General': 'Alto',
    # ... más datos
}

# Generar recomendaciones
recommendations = recommender.recommend_careers(student_data, top_n=5)

# Mostrar resultados
for rec in recommendations:
    print(f"{rec['nombre']}: {rec['puntuacion']:.1%} compatibilidad")
```

## 🎯 Algoritmo de Recomendación

1. **Predicción de Perfil**: Usa modelo ML para predecir personalidad vocacional
2. **Predicción de Sector**: Usa modelo ML para predecir sector laboral preferido
3. **Filtrado de Carreras**: Encuentra carreras que coincidan con predicciones
4. **Puntuación**: Calcula compatibilidad basada en:
   - Coincidencia con perfil y sector
   - Confianza de las predicciones
   - Requisitos académicos
5. **Ranking**: Ordena carreras por puntuación de compatibilidad

## 📈 Mejoras Futuras

- [ ] Interfaz web con Flask/Django
- [ ] Más carreras universitarias
- [ ] Integración con APIs de universidades
- [ ] Análisis de tendencias del mercado laboral
- [ ] Recomendaciones de universidades específicas
- [ ] Sistema de feedback de usuarios

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- Tu nombre - Desarrollo inicial

## 🙏 Agradecimientos

- Universidades colombianas por la información de carreras
- Comunidad de scikit-learn por las herramientas de ML
- Estudiantes que proporcionaron datos para el entrenamiento

---

¡Esperamos que este sistema te ayude a encontrar la carrera perfecta! 🎓✨
