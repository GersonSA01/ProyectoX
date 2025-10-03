from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Asignatura, ProgramaAnalitico, Unidad


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para demostrar el sistema de generación automática de preguntas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--asignaturas',
            type=int,
            default=3,
            help='Número de asignaturas a crear (default: 3)'
        )
        parser.add_argument(
            '--programas-por-asignatura',
            type=int,
            default=2,
            help='Número de programas por asignatura (default: 2)'
        )
        parser.add_argument(
            '--unidades-por-programa',
            type=int,
            default=5,
            help='Número de unidades por programa (default: 5)'
        )

    def handle(self, *args, **options):
        asignaturas_count = options['asignaturas']
        programas_count = options['programas_por_asignatura']
        unidades_count = options['unidades_por_programa']

        self.stdout.write(
            self.style.SUCCESS(
                f'Creando datos de ejemplo: {asignaturas_count} asignaturas, '
                f'{programas_count} programas/asignatura, {unidades_count} unidades/programa'
            )
        )

        with transaction.atomic():
            # Crear asignaturas
            asignaturas = self.crear_asignaturas(asignaturas_count)
            
            # Crear programas analíticos
            programas = self.crear_programas(asignaturas, programas_count)
            
            # Crear unidades
            unidades = self.crear_unidades(programas, unidades_count)
            
            # Generar preguntas automáticamente
            self.generar_preguntas_automaticamente(unidades)

        total_preguntas = sum(unidad.num_preguntas for unidad in unidades)
        self.stdout.write(
            self.style.SUCCESS(
                f'¡Datos creados exitosamente! Total de preguntas generadas: {total_preguntas}'
            )
        )


    def crear_asignaturas(self, count):
        """Crear asignaturas de ejemplo"""
        asignaturas_ejemplo = [
            'Matemáticas',
            'Ciencias Naturales',
            'Historia',
            'Literatura',
            'Inglés',
            'Educación Física',
            'Arte',
            'Música',
            'Tecnología',
            'Geografía'
        ]

        asignaturas = []
        for i in range(count):
            nombre = asignaturas_ejemplo[i % len(asignaturas_ejemplo)]
            if i > 0:
                nombre += f" {i+1}"
            
            asignatura, created = Asignatura.objects.get_or_create(
                descripcion=nombre
            )
            asignaturas.append(asignatura)

        self.stdout.write(f'Asignaturas creadas: {len(asignaturas)}')
        return asignaturas

    def crear_programas(self, asignaturas, count):
        """Crear programas analíticos de ejemplo"""
        programas = []
        for asignatura in asignaturas:
            for i in range(count):
                titulo = f"Programa Analítico {i+1} - {asignatura.descripcion}"
                contexto = f"Este programa analítico cubre los aspectos fundamentales de {asignatura.descripcion} en el nivel educativo correspondiente."
                
                programa, created = ProgramaAnalitico.objects.get_or_create(
                    titulo=titulo,
                    defaults={
                        'contexto': contexto,
                        'asignatura': asignatura
                    }
                )
                programas.append(programa)

        self.stdout.write(f'Programas creados: {len(programas)}')
        return programas

    def crear_unidades(self, programas, count):
        """Crear unidades de ejemplo"""
        import random
        unidades = []

        for programa in programas:
            for i in range(count):
                descripcion = f"Unidad {i+1}: Conceptos Fundamentales de {programa.asignatura.descripcion}"
                num_preguntas = random.randint(5, 15)  # Entre 5 y 15 preguntas por unidad
                
                unidad, created = Unidad.objects.get_or_create(
                    numero_unidad=i+1,
                    programa_analitico=programa,
                    defaults={
                        'descripcion': descripcion,
                        'num_preguntas': num_preguntas
                    }
                )
                unidades.append(unidad)

        self.stdout.write(f'Unidades creadas: {len(unidades)}')
        return unidades

    def generar_preguntas_automaticamente(self, unidades):
        """Generar preguntas automáticamente para todas las unidades"""
        total_generadas = 0
        for unidad in unidades:
            if unidad.generar_preguntas_automaticamente():
                total_generadas += unidad.num_preguntas
                self.stdout.write(f'  OK {unidad.num_preguntas} preguntas generadas para {unidad}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ERROR: Error generando preguntas para {unidad}')
                )

        self.stdout.write(f'Total preguntas generadas: {total_generadas}')
