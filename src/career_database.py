"""
Base de datos de carreras universitarias reales con mapeo a perfiles y sectores
"""

import json
from typing import Dict, List, Tuple
import pandas as pd

class CareerDatabase:
    """
    Base de datos de carreras universitarias con mapeo a perfiles vocacionales
    """
    
    def __init__(self):
        self.careers = self._load_career_data()
    
    def _load_career_data(self) -> Dict:
        """
        Carga la base de datos de carreras universitarias reales
        """
        careers = {
            # CARRERAS TÉCNICAS E INGENIERÍA
            "Ingeniería de Sistemas": {
                "perfil_personalidad": ["Técnico", "Investigador"],
                "sector_preferido": ["Tecnología", "Industrial"],
                "descripcion": "Diseño, desarrollo e implementación de sistemas de información y software",
                "duracion": "5 años",
                "modalidad": ["Presencial", "Virtual"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Alto",
                    "ciencias": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Norte",
                    "Universidad EAFIT"
                ],
                "campo_laboral": [
                    "Desarrollo de software",
                    "Administración de sistemas",
                    "Consultoría tecnológica",
                    "Gestión de proyectos TI"
                ],
                "salario_promedio": "3.500.000 - 8.000.000 COP"
            },
            
            "Ingeniería Civil": {
                "perfil_personalidad": ["Técnico", "Organizador"],
                "sector_preferido": ["Industrial", "Tecnología"],
                "descripcion": "Diseño, construcción y mantenimiento de infraestructura civil",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Alto",
                    "ciencias": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Valle",
                    "Universidad Industrial de Santander"
                ],
                "campo_laboral": [
                    "Construcción de edificaciones",
                    "Infraestructura vial",
                    "Gestión de proyectos",
                    "Consultoría estructural"
                ],
                "salario_promedio": "3.000.000 - 7.000.000 COP"
            },
            
            "Ingeniería Biomédica": {
                "perfil_personalidad": ["Técnico", "Investigador"],
                "sector_preferido": ["Salud", "Tecnología"],
                "descripcion": "Aplicación de principios de ingeniería a la medicina y biología",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Alto",
                    "biologia": "Alto"
                },
                "universidades": [
                    "Universidad de los Andes",
                    "Universidad EIA",
                    "Universidad CES",
                    "Universidad del Rosario"
                ],
                "campo_laboral": [
                    "Diseño de equipos médicos",
                    "Investigación biomédica",
                    "Gestión hospitalaria",
                    "Desarrollo de prótesis"
                ],
                "salario_promedio": "3.500.000 - 7.500.000 COP"
            },
            
            "Ingeniería Mecánica": {
                "perfil_personalidad": ["Técnico", "Organizador"],
                "sector_preferido": ["Industrial", "Tecnología"],
                "descripcion": "Diseño, fabricación y mantenimiento de sistemas mecánicos",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Alto",
                    "ciencias": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Valle",
                    "Universidad Industrial de Santander"
                ],
                "campo_laboral": [
                    "Diseño de maquinaria",
                    "Manufactura industrial",
                    "Mantenimiento industrial",
                    "Consultoría técnica"
                ],
                "salario_promedio": "3.200.000 - 7.500.000 COP"
            },
            
            "Ingeniería Eléctrica": {
                "perfil_personalidad": ["Técnico", "Investigador"],
                "sector_preferido": ["Tecnología", "Industrial"],
                "descripcion": "Diseño y gestión de sistemas eléctricos y electrónicos",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Alto",
                    "ciencias": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Valle",
                    "Universidad Industrial de Santander"
                ],
                "campo_laboral": [
                    "Sistemas de potencia",
                    "Electrónica industrial",
                    "Automatización",
                    "Energías renovables"
                ],
                "salario_promedio": "3.500.000 - 8.000.000 COP"
            },
            
            "Ingeniería Química": {
                "perfil_personalidad": ["Técnico", "Investigador"],
                "sector_preferido": ["Industrial", "Investigación"],
                "descripcion": "Diseño y optimización de procesos químicos industriales",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "quimica": "Alto",
                    "matematicas": "Alto",
                    "fisica": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad Industrial de Santander"
                ],
                "campo_laboral": [
                    "Industria petroquímica",
                    "Procesos industriales",
                    "Control de calidad",
                    "Investigación y desarrollo"
                ],
                "salario_promedio": "3.800.000 - 8.500.000 COP"
            },
            
            # CARRERAS DE SALUD
            "Medicina": {
                "perfil_personalidad": ["Investigador", "Social"],
                "sector_preferido": ["Salud"],
                "descripcion": "Diagnóstico, tratamiento y prevención de enfermedades",
                "duracion": "6 años + especialización",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "biologia": "Alto",
                    "quimica": "Alto",
                    "matematicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de Antioquia",
                    "Universidad Javeriana",
                    "Universidad del Rosario",
                    "Universidad CES"
                ],
                "campo_laboral": [
                    "Atención clínica",
                    "Investigación médica",
                    "Salud pública",
                    "Especialidades médicas"
                ],
                "salario_promedio": "4.000.000 - 15.000.000 COP"
            },
            
            "Enfermería": {
                "perfil_personalidad": ["Social", "Organizador"],
                "sector_preferido": ["Salud"],
                "descripcion": "Cuidado integral de la salud de individuos y comunidades",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "biologia": "Alto",
                    "quimica": "Medio",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de Antioquia",
                    "Universidad Javeriana",
                    "Universidad del Norte",
                    "Universidad El Bosque"
                ],
                "campo_laboral": [
                    "Atención hospitalaria",
                    "Cuidados intensivos",
                    "Salud comunitaria",
                    "Administración en salud"
                ],
                "salario_promedio": "2.800.000 - 5.500.000 COP"
            },
            
            "Odontología": {
                "perfil_personalidad": ["Técnico", "Social"],
                "sector_preferido": ["Salud"],
                "descripcion": "Salud bucal y tratamiento dental integral",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "biologia": "Alto",
                    "quimica": "Medio",
                    "matematicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de Antioquia",
                    "Universidad Javeriana",
                    "Universidad del Valle",
                    "Universidad CES"
                ],
                "campo_laboral": [
                    "Clínica dental",
                    "Ortodoncia",
                    "Cirugía oral",
                    "Salud pública dental"
                ],
                "salario_promedio": "3.500.000 - 8.000.000 COP"
            },
            
            "Fisioterapia": {
                "perfil_personalidad": ["Social", "Técnico"],
                "sector_preferido": ["Salud"],
                "descripcion": "Rehabilitación y recuperación funcional de pacientes",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "biologia": "Alto",
                    "fisica": "Medio",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de Antioquia",
                    "Universidad Javeriana",
                    "Universidad del Valle",
                    "Universidad El Bosque"
                ],
                "campo_laboral": [
                    "Rehabilitación física",
                    "Deportología",
                    "Fisioterapia pediátrica",
                    "Fisioterapia geriátrica"
                ],
                "salario_promedio": "2.500.000 - 5.000.000 COP"
            },
            
            "Psicología": {
                "perfil_personalidad": ["Social", "Investigador"],
                "sector_preferido": ["Salud", "Educativo"],
                "descripcion": "Estudio del comportamiento humano y procesos mentales",
                "duracion": "5 años",
                "modalidad": ["Presencial", "Virtual"],
                "requisitos_academicos": {
                    "ciencias_sociales": "Alto",
                    "biologia": "Medio",
                    "matematicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Norte",
                    "Universidad Konrad Lorenz"
                ],
                "campo_laboral": [
                    "Psicología clínica",
                    "Psicología organizacional",
                    "Psicología educativa",
                    "Investigación psicológica"
                ],
                "salario_promedio": "2.500.000 - 6.000.000 COP"
            },
            
            # CARRERAS EDUCATIVAS
            "Licenciatura en Matemáticas": {
                "perfil_personalidad": ["Investigador", "Social"],
                "sector_preferido": ["Educativo"],
                "descripcion": "Formación de docentes especializados en matemáticas",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Medio",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad Pedagógica Nacional",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad de Nariño"
                ],
                "campo_laboral": [
                    "Docencia en matemáticas",
                    "Investigación matemática",
                    "Desarrollo curricular",
                    "Tutoría académica"
                ],
                "salario_promedio": "2.200.000 - 4.500.000 COP"
            },
            
            "Licenciatura en Ciencias Naturales": {
                "perfil_personalidad": ["Investigador", "Social"],
                "sector_preferido": ["Educativo", "Investigación"],
                "descripcion": "Formación de docentes en ciencias naturales y biología",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "biologia": "Alto",
                    "quimica": "Alto",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad Pedagógica Nacional",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad de Nariño"
                ],
                "campo_laboral": [
                    "Docencia en ciencias",
                    "Investigación científica",
                    "Educación ambiental",
                    "Desarrollo curricular"
                ],
                "salario_promedio": "2.200.000 - 4.500.000 COP"
            },
            
            "Licenciatura en Lengua Castellana": {
                "perfil_personalidad": ["Social", "Artístico"],
                "sector_preferido": ["Educativo", "Cultural"],
                "descripcion": "Formación de docentes en lengua castellana y literatura",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "lengua_castellana": "Alto",
                    "ciencias_sociales": "Alto",
                    "educacion_artistica": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad Pedagógica Nacional",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad de Nariño"
                ],
                "campo_laboral": [
                    "Docencia en lengua",
                    "Edición literaria",
                    "Comunicación escrita",
                    "Desarrollo curricular"
                ],
                "salario_promedio": "2.200.000 - 4.500.000 COP"
            },
            
            "Licenciatura en Ciencias Sociales": {
                "perfil_personalidad": ["Social", "Investigador"],
                "sector_preferido": ["Educativo", "Cultural"],
                "descripcion": "Formación de docentes en ciencias sociales e historia",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "ciencias_sociales": "Alto",
                    "lengua_castellana": "Alto",
                    "ciencias_economicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad Pedagógica Nacional",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad de Nariño"
                ],
                "campo_laboral": [
                    "Docencia en ciencias sociales",
                    "Investigación histórica",
                    "Desarrollo comunitario",
                    "Desarrollo curricular"
                ],
                "salario_promedio": "2.200.000 - 4.500.000 COP"
            },
            
            # CARRERAS DE ADMINISTRACIÓN Y NEGOCIOS
            "Administración de Empresas": {
                "perfil_personalidad": ["Organizador", "Líder"],
                "sector_preferido": ["Financiero", "Industrial"],
                "descripcion": "Gestión y administración de organizaciones empresariales",
                "duracion": "4 años",
                "modalidad": ["Presencial", "Virtual"],
                "requisitos_academicos": {
                    "matematicas": "Medio",
                    "ciencias_economicas": "Alto",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad EAFIT",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Gerencia empresarial",
                    "Consultoría organizacional",
                    "Emprendimiento",
                    "Recursos humanos"
                ],
                "salario_promedio": "3.000.000 - 10.000.000 COP"
            },
            
            "Contaduría Pública": {
                "perfil_personalidad": ["Organizador", "Técnico"],
                "sector_preferido": ["Financiero"],
                "descripcion": "Contabilidad, auditoría y finanzas empresariales",
                "duracion": "4 años",
                "modalidad": ["Presencial", "Virtual"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "ciencias_economicas": "Alto",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad EAFIT",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Contabilidad empresarial",
                    "Auditoría financiera",
                    "Consultoría fiscal",
                    "Análisis financiero"
                ],
                "salario_promedio": "2.800.000 - 8.000.000 COP"
            },
            
            "Economía": {
                "perfil_personalidad": ["Investigador", "Organizador"],
                "sector_preferido": ["Financiero", "Investigación"],
                "descripcion": "Análisis de fenómenos económicos y políticas públicas",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "ciencias_economicas": "Alto",
                    "ciencias_sociales": "Alto"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad EAFIT",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Análisis económico",
                    "Políticas públicas",
                    "Investigación económica",
                    "Consultoría financiera"
                ],
                "salario_promedio": "3.500.000 - 9.000.000 COP"
            },
            
            "Mercadeo": {
                "perfil_personalidad": ["Social", "Líder"],
                "sector_preferido": ["Financiero", "Industrial"],
                "descripcion": "Estrategias de comercialización y gestión de marca",
                "duracion": "4 años",
                "modalidad": ["Presencial", "Virtual"],
                "requisitos_academicos": {
                    "ciencias_sociales": "Alto",
                    "ciencias_economicas": "Medio",
                    "lengua_castellana": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad EAFIT",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Marketing digital",
                    "Investigación de mercados",
                    "Gestión de marca",
                    "Ventas estratégicas"
                ],
                "salario_promedio": "2.800.000 - 7.500.000 COP"
            },
            
            # CARRERAS DE DERECHO Y CIENCIAS POLÍTICAS
            "Derecho": {
                "perfil_personalidad": ["Líder", "Social"],
                "sector_preferido": ["Servicios", "Cultural"],
                "descripcion": "Estudio del sistema legal y administración de justicia",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "lengua_castellana": "Alto",
                    "ciencias_sociales": "Alto",
                    "ciencias_economicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Rosario",
                    "Universidad Externado"
                ],
                "campo_laboral": [
                    "Abogacía privada",
                    "Fiscalía",
                    "Consultoría legal",
                    "Derecho internacional"
                ],
                "salario_promedio": "3.000.000 - 12.000.000 COP"
            },
            
            "Ciencia Política": {
                "perfil_personalidad": ["Líder", "Investigador"],
                "sector_preferido": ["Servicios", "Cultural"],
                "descripcion": "Análisis de sistemas políticos y políticas públicas",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "ciencias_sociales": "Alto",
                    "ciencias_economicas": "Alto",
                    "lengua_castellana": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Rosario",
                    "Universidad Externado"
                ],
                "campo_laboral": [
                    "Análisis político",
                    "Diplomacia",
                    "Consultoría política",
                    "Investigación social"
                ],
                "salario_promedio": "2.800.000 - 8.000.000 COP"
            },
            
            "Relaciones Internacionales": {
                "perfil_personalidad": ["Social", "Líder"],
                "sector_preferido": ["Servicios", "Cultural"],
                "descripcion": "Gestión de relaciones diplomáticas y comercio internacional",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "ciencias_sociales": "Alto",
                    "lengua_castellana": "Alto",
                    "ciencias_economicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Rosario",
                    "Universidad Externado"
                ],
                "campo_laboral": [
                    "Diplomacia",
                    "Comercio internacional",
                    "Organizaciones multilaterales",
                    "Consultoría internacional"
                ],
                "salario_promedio": "3.200.000 - 8.500.000 COP"
            },
            
            # CARRERAS DE INVESTIGACIÓN
            "Biología": {
                "perfil_personalidad": ["Investigador", "Técnico"],
                "sector_preferido": ["Investigación", "Salud"],
                "descripcion": "Estudio de los seres vivos y procesos biológicos",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "biologia": "Alto",
                    "quimica": "Alto",
                    "matematicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Valle",
                    "Universidad de Antioquia"
                ],
                "campo_laboral": [
                    "Investigación científica",
                    "Laboratorios clínicos",
                    "Conservación ambiental",
                    "Docencia universitaria"
                ],
                "salario_promedio": "2.800.000 - 6.500.000 COP"
            },
            
            "Química": {
                "perfil_personalidad": ["Investigador", "Técnico"],
                "sector_preferido": ["Investigación", "Industrial"],
                "descripcion": "Estudio de la materia, sus propiedades y transformaciones",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "quimica": "Alto",
                    "matematicas": "Alto",
                    "fisica": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad Industrial de Santander"
                ],
                "campo_laboral": [
                    "Investigación química",
                    "Industria farmacéutica",
                    "Control de calidad",
                    "Desarrollo de productos"
                ],
                "salario_promedio": "3.000.000 - 7.000.000 COP"
            },
            
            "Física": {
                "perfil_personalidad": ["Investigador", "Técnico"],
                "sector_preferido": ["Investigación", "Tecnología"],
                "descripcion": "Estudio de las leyes fundamentales del universo",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "fisica": "Alto",
                    "matematicas": "Alto",
                    "quimica": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad Industrial de Santander"
                ],
                "campo_laboral": [
                    "Investigación científica",
                    "Astronomía",
                    "Física aplicada",
                    "Docencia universitaria"
                ],
                "salario_promedio": "3.200.000 - 7.500.000 COP"
            },
            
            "Geología": {
                "perfil_personalidad": ["Investigador", "Técnico"],
                "sector_preferido": ["Investigación", "Industrial"],
                "descripcion": "Estudio de la estructura y composición de la Tierra",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "fisica": "Alto",
                    "quimica": "Alto",
                    "matematicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad de Antioquia",
                    "Universidad del Valle",
                    "Universidad Industrial de Santander"
                ],
                "campo_laboral": [
                    "Exploración minera",
                    "Geología ambiental",
                    "Investigación geológica",
                    "Consultoría geotécnica"
                ],
                "salario_promedio": "3.500.000 - 8.000.000 COP"
            },
            
            # CARRERAS TECNOLÓGICAS ESPECIALIZADAS
            "Ingeniería de Software": {
                "perfil_personalidad": ["Técnico", "Investigador"],
                "sector_preferido": ["Tecnología"],
                "descripcion": "Desarrollo y mantenimiento de sistemas de software",
                "duracion": "4-5 años",
                "modalidad": ["Presencial", "Virtual"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Medio",
                    "ciencias": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad EAFIT",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Desarrollo de aplicaciones",
                    "Arquitectura de software",
                    "DevOps",
                    "Gestión de proyectos TI"
                ],
                "salario_promedio": "3.800.000 - 9.000.000 COP"
            },
            
            "Ingeniería en Telecomunicaciones": {
                "perfil_personalidad": ["Técnico", "Investigador"],
                "sector_preferido": ["Tecnología"],
                "descripcion": "Diseño y gestión de sistemas de comunicación",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "matematicas": "Alto",
                    "fisica": "Alto",
                    "ciencias": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad EAFIT",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Redes de telecomunicaciones",
                    "Sistemas de comunicación",
                    "Tecnología móvil",
                    "Consultoría en telecomunicaciones"
                ],
                "salario_promedio": "3.500.000 - 8.500.000 COP"
            },
            
            "Ingeniería en Multimedia": {
                "perfil_personalidad": ["Artístico", "Técnico"],
                "sector_preferido": ["Tecnología", "Cultural"],
                "descripcion": "Desarrollo de contenidos digitales interactivos",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "educacion_artistica": "Alto",
                    "matematicas": "Medio",
                    "ciencias": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad EAFIT",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Desarrollo de videojuegos",
                    "Animación digital",
                    "Diseño web",
                    "Producción multimedia"
                ],
                "salario_promedio": "3.000.000 - 7.500.000 COP"
            },
            
            # CARRERAS ARTÍSTICAS Y CULTURALES
            "Diseño Gráfico": {
                "perfil_personalidad": ["Artístico", "Técnico"],
                "sector_preferido": ["Cultural", "Industrial"],
                "descripcion": "Creación de identidades visuales y comunicación gráfica",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "educacion_artistica": "Alto",
                    "lengua_castellana": "Medio",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad Jorge Tadeo Lozano",
                    "Universidad de Palermo"
                ],
                "campo_laboral": [
                    "Diseño de marca",
                    "Ilustración digital",
                    "Publicidad",
                    "Editorial"
                ],
                "salario_promedio": "2.500.000 - 6.500.000 COP"
            },
            
            "Música": {
                "perfil_personalidad": ["Artístico", "Social"],
                "sector_preferido": ["Cultural"],
                "descripcion": "Formación musical profesional y composición",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "educacion_artistica": "Alto",
                    "lengua_castellana": "Medio",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad El Bosque",
                    "Universidad de Antioquia"
                ],
                "campo_laboral": [
                    "Interpretación musical",
                    "Composición",
                    "Docencia musical",
                    "Producción musical"
                ],
                "salario_promedio": "2.200.000 - 5.500.000 COP"
            },
            
            "Diseño Industrial": {
                "perfil_personalidad": ["Artístico", "Técnico"],
                "sector_preferido": ["Industrial", "Cultural"],
                "descripcion": "Diseño de productos industriales y objetos de uso cotidiano",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "educacion_artistica": "Alto",
                    "matematicas": "Medio",
                    "fisica": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad Jorge Tadeo Lozano",
                    "Universidad de Palermo"
                ],
                "campo_laboral": [
                    "Diseño de productos",
                    "Innovación industrial",
                    "Consultoría en diseño",
                    "Desarrollo de prototipos"
                ],
                "salario_promedio": "3.200.000 - 7.500.000 COP"
            },
            
            "Arquitectura": {
                "perfil_personalidad": ["Artístico", "Técnico"],
                "sector_preferido": ["Industrial", "Cultural"],
                "descripcion": "Diseño de espacios arquitectónicos y urbanos",
                "duracion": "5 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "educacion_artistica": "Alto",
                    "matematicas": "Medio",
                    "fisica": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad Jorge Tadeo Lozano",
                    "Universidad de Palermo"
                ],
                "campo_laboral": [
                    "Diseño arquitectónico",
                    "Urbanismo",
                    "Restauración patrimonial",
                    "Consultoría arquitectónica"
                ],
                "salario_promedio": "3.500.000 - 8.500.000 COP"
            },
            
            "Comunicación Social": {
                "perfil_personalidad": ["Social", "Artístico"],
                "sector_preferido": ["Cultural", "Servicios"],
                "descripcion": "Gestión de la comunicación y medios masivos",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "lengua_castellana": "Alto",
                    "ciencias_sociales": "Alto",
                    "educacion_artistica": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad Jorge Tadeo Lozano",
                    "Universidad del Norte"
                ],
                "campo_laboral": [
                    "Periodismo",
                    "Producción audiovisual",
                    "Relaciones públicas",
                    "Marketing digital"
                ],
                "salario_promedio": "2.800.000 - 6.500.000 COP"
            },
            
            # CARRERAS DE SERVICIOS Y TURISMO
            "Administración Turística y Hotelera": {
                "perfil_personalidad": ["Social", "Organizador"],
                "sector_preferido": ["Servicios"],
                "descripcion": "Gestión de servicios turísticos y hoteleros",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "ciencias_sociales": "Alto",
                    "lengua_castellana": "Alto",
                    "ciencias_economicas": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Norte",
                    "Universidad Externado"
                ],
                "campo_laboral": [
                    "Gestión hotelera",
                    "Turismo receptivo",
                    "Eventos y convenciones",
                    "Consultoría turística"
                ],
                "salario_promedio": "2.500.000 - 5.500.000 COP"
            },
            
            "Gastronomía": {
                "perfil_personalidad": ["Artístico", "Social"],
                "sector_preferido": ["Servicios", "Cultural"],
                "descripcion": "Arte culinario y gestión de servicios gastronómicos",
                "duracion": "4 años",
                "modalidad": ["Presencial"],
                "requisitos_academicos": {
                    "educacion_artistica": "Alto",
                    "quimica": "Medio",
                    "ciencias_sociales": "Medio"
                },
                "universidades": [
                    "Universidad Nacional de Colombia",
                    "Universidad de los Andes",
                    "Universidad Javeriana",
                    "Universidad del Norte",
                    "Universidad Externado"
                ],
                "campo_laboral": [
                    "Chef profesional",
                    "Gestión de restaurantes",
                    "Consultoría gastronómica",
                    "Investigación culinaria"
                ],
                "salario_promedio": "2.800.000 - 6.000.000 COP"
            }
        }
        
        return careers
    
    def get_careers_by_profile(self, perfil_personalidad: str) -> List[str]:
        """
        Obtiene carreras que coinciden con un perfil de personalidad
        """
        matching_careers = []
        for career_name, career_data in self.careers.items():
            if perfil_personalidad in career_data["perfil_personalidad"]:
                matching_careers.append(career_name)
        return matching_careers
    
    def get_careers_by_sector(self, sector_preferido: str) -> List[str]:
        """
        Obtiene carreras que coinciden con un sector preferido
        """
        matching_careers = []
        for career_name, career_data in self.careers.items():
            if sector_preferido in career_data["sector_preferido"]:
                matching_careers.append(career_name)
        return matching_careers
    
    def get_career_info(self, career_name: str) -> Dict:
        """
        Obtiene información detallada de una carrera
        """
        return self.careers.get(career_name, {})
    
    def get_all_careers(self) -> List[str]:
        """
        Obtiene lista de todas las carreras disponibles
        """
        return list(self.careers.keys())
    
    def save_to_json(self, filepath: str = "data/careers_database.json"):
        """
        Guarda la base de datos en formato JSON
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.careers, f, ensure_ascii=False, indent=2)
        print(f"Base de datos de carreras guardada en: {filepath}")


def main():
    """
    Función principal para crear y guardar la base de datos de carreras
    """
    print("=== CREANDO BASE DE DATOS DE CARRERAS ===")
    
    # Crear instancia de la base de datos
    career_db = CareerDatabase()
    
    # Mostrar estadísticas
    total_careers = len(career_db.get_all_careers())
    print(f"Total de carreras en la base de datos: {total_careers}")
    
    # Mostrar carreras por perfil
    perfiles = ["Investigador", "Técnico", "Artístico", "Organizador", "Líder", "Social"]
    for perfil in perfiles:
        careers = career_db.get_careers_by_profile(perfil)
        print(f"\nCarreras para perfil '{perfil}': {len(careers)}")
        for career in careers[:3]:  # Mostrar solo las primeras 3
            print(f"  - {career}")
    
    # Guardar en archivo JSON
    career_db.save_to_json()
    
    print("\n=== BASE DE DATOS CREADA EXITOSAMENTE ===")


if __name__ == "__main__":
    main() 