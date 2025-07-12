# Proyecto mIA - Generador de Datos Educativos

## Descripción

Este proyecto genera datos simulados de estudiantes para análisis educativo, incluyendo respuestas de formularios de orientación socio-ocupacional y notas académicas trimestrales.

## Estructura del Proyecto

```
mIA/
├── data/                    # Datos generados
│   ├── respuestas_formulario.csv
│   ├── notas_academicas.csv
│   └── generated_answers.csv
├── src/                     # Código fuente
│   ├── ans_generator.py
│   ├── form_structure.json
│   └── requirements.txt
├── reports/                 # Reportes y gráficas
├── app/                     # Aplicación Streamlit (futuro)
├── README.md
└── .gitignore
```

## Características

### Datos Generados

- **respuestas_formulario.csv**: Respuestas del formulario de orientación socio-ocupacional
- **notas_academicas.csv**: Notas trimestrales de 8 materias (escala 1-5)

### Funcionalidades

- Generación de perfiles estudiantiles realistas
- Coherencia entre preferencias y rendimiento académico
- Sistema de promoción académica realista
- Escala de calificaciones colombiana (1-5, 3.0 mínimo aprobatorio)

### Materias Incluidas

- Física
- Biología y química
- Educación artística
- Ciencias sociales
- Educación física
- Matemáticas
- Lengua castellana
- Ciencias económicas y políticas

## Uso

### Generar Datos

```bash
cd src
python ans_generator.py
```

### Estructura de Datos

- **70%** de estudiantes aprueban todas las materias
- **20%** reprueban 1-2 materias
- **10%** reprueban 3+ materias (no promovidos)

## Dependencias

- pandas
- faker
- random
- json

## Instalación

```bash
pip install -r src/requirements.txt
```
