from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
import json

from .repositories import (
    CarreraRepository, AsignaturaRepository, ProgramaAnaliticoRepository,
    UnidadRepository, PreguntaRepository, OpcionRepository, PartidaRepository
)
from .supabase_client import get_supabase_client


# ============================================================================
# VISTAS PRINCIPALES - SUPABASE
# ============================================================================

class PartidaListView(ListView):
    """Lista de partidas con contador de unidades - Supabase"""
    template_name = 'partidas/lista.html'
    context_object_name = 'partidas'
    paginate_by = 50

    def get_queryset(self):
        partidas = PartidaRepository.list_all(limit=1000)
        for partida in partidas:
            # Obtener asignatura
            asignatura = AsignaturaRepository.get_by_id(partida['asignatura_id'])
            if asignatura:
                partida['asignatura'] = asignatura

                # Obtener carrera si existe
                if asignatura.get('carrera_id'):
                    carrera = CarreraRepository.get_by_id(asignatura['carrera_id'])
                    if carrera:
                        partida['asignatura']['carrera'] = carrera

                # Calcular unidades
                programas = ProgramaAnaliticoRepository.list_by_asignatura(
                    asignatura_id=asignatura['asignatura_id']
                )
                total_unidades = 0
                for programa in programas:
                    unidades = UnidadRepository.list_all(
                        limit=1000,
                        programa_analitico_id=programa['linea_educativa_id']
                    )
                    total_unidades += len(unidades)
                partida['unidades_count'] = total_unidades
            else:
                partida['unidades_count'] = 0
                partida['asignatura'] = None

        return partidas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Datos para el modal de crear partida
        context['asignaturas'] = AsignaturaRepository.list_all(limit=1000)
        context['carreras'] = CarreraRepository.list_all(limit=1000)
        return context


class UnidadListView(ListView):
    """Lista de unidades con filtros - Supabase"""
    template_name = 'unidades/lista.html'
    context_object_name = 'unidades'
    paginate_by = 50

    def get_queryset(self):
        # Obtener filtro de la URL
        programa_analitico_id = self.request.GET.get('programa_analitico')

        # Obtener unidades según el filtro
        if programa_analitico_id:
            unidades = UnidadRepository.list_all(
                limit=1000,
                programa_analitico_id=int(programa_analitico_id)
            )
        else:
            unidades = UnidadRepository.list_all(limit=1000)

        # Enriquecer datos de cada unidad
        for unidad in unidades:
            # Obtener programa analítico
            programa = ProgramaAnaliticoRepository.get_by_id(unidad['programa_analitico_id'])
            if programa:
                unidad['programa_analitico'] = programa

                # Obtener asignatura
                asignatura = AsignaturaRepository.get_by_id(programa['asignatura_id'])
                if asignatura:
                    unidad['programa_analitico']['asignatura'] = asignatura

                    # Obtener carrera si existe
                    if asignatura.get('carrera_id'):
                        carrera = CarreraRepository.get_by_id(asignatura['carrera_id'])
                        if carrera:
                            unidad['programa_analitico']['asignatura']['carrera'] = carrera

        return unidades

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Datos para el filtro de programas analíticos
        context['programas_analiticos'] = ProgramaAnaliticoRepository.list_all(limit=1000)

        # Enriquecer programas con asignatura y carrera
        for programa in context['programas_analiticos']:
            asignatura = AsignaturaRepository.get_by_id(programa['asignatura_id'])
            if asignatura:
                programa['asignatura'] = asignatura
                if asignatura.get('carrera_id'):
                    carrera = CarreraRepository.get_by_id(asignatura['carrera_id'])
                    if carrera:
                        programa['asignatura']['carrera'] = carrera

        return context


class PreguntaListView(ListView):
    """Lista de preguntas con filtros - Supabase"""
    template_name = 'preguntas/lista.html'
    context_object_name = 'preguntas'
    paginate_by = 50

    def get_queryset(self):
        partida_id = self.request.GET.get('partida')
        if not partida_id:
            return []

        partida = PartidaRepository.get_by_id(int(partida_id))
        if not partida:
            return []

        asignatura = AsignaturaRepository.get_by_id(partida['asignatura_id'])
        if not asignatura:
            return []

        programas = ProgramaAnaliticoRepository.list_by_asignatura(
            asignatura_id=asignatura['asignatura_id']
        )

        programa_analitico_id = self.request.GET.get('programa_analitico')
        if programa_analitico_id:
            programas = [p for p in programas if p['linea_educativa_id'] == int(programa_analitico_id)]

        todas_unidades = []
        for programa in programas:
            unidades = UnidadRepository.list_all(
                limit=1000,
                programa_analitico_id=programa['linea_educativa_id']
            )
            todas_unidades.extend(unidades)

        unidad_id = self.request.GET.get('unidad')
        if unidad_id:
            todas_unidades = [u for u in todas_unidades if u['unidad_id'] == int(unidad_id)]

        todas_preguntas = []
        for unidad in todas_unidades:
            preguntas = PreguntaRepository.list_all(limit=1000, unidad_id=unidad['unidad_id'])
            for pregunta in preguntas:
                pregunta['unidad'] = unidad
                programa_correspondiente = next(
                    (p for p in programas if p['linea_educativa_id'] == unidad['programa_analitico_id']),
                    None
                )
                if programa_correspondiente:
                    pregunta['programa_analitico'] = programa_correspondiente
                    pregunta['asignatura'] = asignatura
                pregunta['opciones'] = OpcionRepository.list_all(limit=1000, pregunta_id=pregunta['pregunta_id'])
            todas_preguntas.extend(preguntas)

        todas_preguntas.sort(key=lambda x: int(x.get('numero', 0)))
        return todas_preguntas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partidas'] = PartidaRepository.list_all(limit=1000)
        context['unidades'] = UnidadRepository.list_all(limit=1000)
        context['programas_analiticos'] = ProgramaAnaliticoRepository.list_all(limit=1000)
        return context


# ============================================================================
# APIs DE EDICIÓN INLINE - SUPABASE
# ============================================================================

@csrf_protect
@require_http_methods(["POST"])
def update_partida_api(request, partida_id):
    """API para actualizar nombre de partida - Supabase"""
    try:
        data = json.loads(request.body)
        if 'descripcion' in data:
            partida = PartidaRepository.update(int(partida_id), descripcion=data['descripcion'])
            return JsonResponse({
                'success': True,
                'message': 'Partida actualizada exitosamente',
                'partida': {
                    'id': partida['partida_id'],
                    'descripcion': partida['descripcion']
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Descripción requerida'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_protect
@require_http_methods(["POST"])
def update_unidad_api(request, unidad_id):
    """API para actualizar descripción de unidad - Supabase"""
    try:
        data = json.loads(request.body)
        if 'descripcion' in data:
            unidad = UnidadRepository.update(int(unidad_id), descripcion=data['descripcion'])
            return JsonResponse({
                'success': True,
                'message': 'Unidad actualizada exitosamente',
                'unidad': {
                    'id': unidad['unidad_id'],
                    'descripcion': unidad['descripcion'],
                    'numero_unidad': unidad['numero_unidad']
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Descripción requerida'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# APIs DE CREACIÓN - SUPABASE
# ============================================================================

@csrf_protect
@require_http_methods(["POST"])
def crear_carrera_ajax(request):
    """API para crear carrera - Supabase"""
    try:
        data = json.loads(request.body)
        descripcion = data.get('descripcion', '').strip()

        if not descripcion:
            return JsonResponse({'success': False, 'error': 'La descripción es requerida'}, status=400)

        carrera = CarreraRepository.create(descripcion=descripcion)
        return JsonResponse({
            'success': True,
            'message': 'Carrera creada exitosamente',
            'carrera': {
                'id': carrera['carrera_id'],
                'descripcion': carrera['descripcion']
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_protect
@require_http_methods(["POST"])
def crear_asignatura_ajax(request):
    """API para crear asignatura - Supabase"""
    try:
        data = json.loads(request.body)
        descripcion = data.get('descripcion', '').strip()
        carrera_id = data.get('carrera_id')

        if not descripcion:
            return JsonResponse({'success': False, 'error': 'La descripción es requerida'}, status=400)

        if not carrera_id:
            return JsonResponse({'success': False, 'error': 'La carrera es requerida'}, status=400)

        asignatura = AsignaturaRepository.create(
            descripcion=descripcion,
            carrera_id=int(carrera_id)
        )
        return JsonResponse({
            'success': True,
            'message': 'Asignatura creada exitosamente',
            'asignatura': {
                'id': asignatura['asignatura_id'],
                'descripcion': asignatura['descripcion'],
                'carrera_id': asignatura['carrera_id']
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# APIs DE FILTROS DINÁMICOS - SUPABASE
# ============================================================================

def get_programas_analiticos(request):
    """API para obtener programas analíticos por partida o por asignatura (Supabase)."""
    try:
        partida_id = request.GET.get('partida_id')
        asignatura_id = request.GET.get('asignatura_id')

        # 1) Si viene partida_id, obtenemos la asignatura desde la partida
        if partida_id:
            try:
                pid = int(partida_id)
            except ValueError:
                return JsonResponse({'error': 'partida_id inválido'}, status=400)

            try:
                partida = PartidaRepository.get_by_id(pid)
                print(f"DEBUG: partida encontrada={partida}")
            except Exception as e:
                print(f"DEBUG: Error al obtener partida: {e}")
                return JsonResponse({'error': f'Error al obtener partida: {e}'}, status=400)

            if not partida:
                print("DEBUG: Partida no encontrada, devolviendo array vacío")
                return JsonResponse([], safe=False)

            # Si la partida existe, usamos su asignatura_id (a menos que ya venga uno explícito)
            asignatura_id = asignatura_id or partida.get('asignatura_id')
            print(f"DEBUG: asignatura_id de partida={asignatura_id}")

        # 2) Validación: necesitamos asignatura_id para listar programas
        if not asignatura_id:
            print("DEBUG: No hay asignatura_id, devolviendo array vacío")
            return JsonResponse([], safe=False)

        try:
            aid = int(asignatura_id)
        except ValueError:
            return JsonResponse({'error': 'asignatura_id inválido'}, status=400)

        # 3) Obtener programas por asignatura
        try:
            programas = ProgramaAnaliticoRepository.list_by_asignatura(asignatura_id=aid)
            print(f"DEBUG: programas encontrados={len(programas) if programas else 0}")
            return JsonResponse(programas or [], safe=False)
        except Exception as e:
            print(f"DEBUG: Error al obtener programas: {e}")
            return JsonResponse({'error': f'Error al obtener programas: {e}'}, status=400)

    except Exception as e:
        print(f"DEBUG: Error general en get_programas_analiticos: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def get_unidades(request):
    """API para obtener unidades por programa analítico - Supabase"""
    try:
        programa_id = request.GET.get('programa_id')
        if not programa_id:
            return JsonResponse([], safe=False)

        unidades = UnidadRepository.list_all(
            limit=1000,
            programa_analitico_id=int(programa_id)
        )
        return JsonResponse(unidades, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_protect
@require_http_methods(["POST"])
def update_pregunta_api(request, pregunta_id):
    """API para actualizar pregunta - Supabase"""
    try:
        data = json.loads(request.body)
        enunciado = data.get('enunciado', '').strip()
        opciones = data.get('opciones', [])

        if not enunciado:
            return JsonResponse({'success': False, 'error': 'Enunciado requerido'}, status=400)

        # Actualizar enunciado de la pregunta
        pregunta = PreguntaRepository.update(int(pregunta_id), enunciado=enunciado)
        if not pregunta:
            return JsonResponse({'success': False, 'error': 'Error al actualizar pregunta'}, status=400)

        # Actualizar opciones
        for opcion_data in opciones:
            opcion_id = opcion_data.get('id')
            texto = opcion_data.get('texto', '').strip()
            es_correcta = opcion_data.get('es_correcta', False)

            if opcion_id and opcion_id != 'new':
                # Actualizar opción existente
                OpcionRepository.update(
                    int(opcion_id),
                    opcion=texto,
                    es_correcta=es_correcta
                )
            elif opcion_id == 'new' and texto:
                # Crear nueva opción
                OpcionRepository.create(
                    opcion=texto,
                    es_correcta=es_correcta,
                    pregunta_id=int(pregunta_id)
                )

        return JsonResponse({
            'success': True,
            'message': 'Pregunta actualizada exitosamente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_protect
@require_http_methods(["DELETE"])
def delete_opcion_api(request, opcion_id):
    """API para eliminar opción - Supabase"""
    try:
        success = OpcionRepository.delete(int(opcion_id))
        if success:
            return JsonResponse({'success': True, 'message': 'Opción eliminada exitosamente'})
        else:
            return JsonResponse({'success': False, 'error': 'Error al eliminar opción'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def obtener_prompt(request):
    """API para obtener prompt de generación de preguntas - Supabase"""
    try:
        partida_id = request.GET.get('partida')
        programa_id = request.GET.get('programa_analitico')
        unidad_id = request.GET.get('unidad')

        if not partida_id:
            return JsonResponse({'success': False, 'error': 'Partida requerida'}, status=400)

        # Obtener datos de la partida
        partida = PartidaRepository.get_by_id(int(partida_id))
        if not partida:
            return JsonResponse({'success': False, 'error': 'Partida no encontrada'}, status=404)

        # Obtener asignatura
        asignatura = AsignaturaRepository.get_by_id(partida['asignatura_id'])
        if not asignatura:
            return JsonResponse({'success': False, 'error': 'Asignatura no encontrada'}, status=404)

        # Obtener carrera
        carrera = None
        if asignatura.get('carrera_id'):
            carrera = CarreraRepository.get_by_id(asignatura['carrera_id'])

        # Obtener programas analíticos
        programas = ProgramaAnaliticoRepository.list_by_asignatura(
            asignatura_id=asignatura['asignatura_id']
        )

        # Obtener unidades y preguntas
        unidades_data = []
        unidad_actual = None  # Para almacenar la unidad actual si se filtra

        for programa in programas:
            unidades = UnidadRepository.list_all(
                limit=1000,
                programa_analitico_id=programa['linea_educativa_id']
            )

            for unidad in unidades:
                # Filtrar por unidad específica si se proporciona
                if unidad_id and unidad['unidad_id'] != int(unidad_id):
                    continue

                # Guardar la unidad actual si se está filtrando por unidad específica
                if unidad_id and unidad['unidad_id'] == int(unidad_id):
                    unidad_actual = {
                        'numero': unidad['numero_unidad'],
                        'descripcion': unidad['descripcion']
                    }

                # Obtener preguntas de la unidad
                preguntas = PreguntaRepository.list_all(limit=1000, unidad_id=unidad['unidad_id'])

                unidad_info = {
                    'numero': unidad['numero_unidad'],
                    'descripcion': unidad['descripcion'],
                    'preguntas': []
                }

                for pregunta in preguntas:
                    # Obtener opciones de la pregunta
                    opciones = OpcionRepository.list_all(limit=1000, pregunta_id=pregunta['pregunta_id'])

                    pregunta_info = {
                        'numero': pregunta['numero'],
                        'enunciado': pregunta['enunciado'],
                        'opciones': []
                    }

                    for opcion in opciones:
                        pregunta_info['opciones'].append({
                            'texto': opcion['opcion'],
                            'es_correcta': opcion['es_correcta']
                        })

                    unidad_info['preguntas'].append(pregunta_info)

                if unidad_info['preguntas']:  # Solo agregar si tiene preguntas
                    unidades_data.append(unidad_info)

        # Generar prompt con información de unidad actual
        prompt = generar_prompt_texto(
            partida, asignatura, carrera, programas, unidades_data, unidad_actual
        )

        return JsonResponse({
            'success': True,
            'prompt': prompt
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def descargar_google_docs(request):
    """API para descargar documento de Google Docs - Supabase"""
    try:
        from django.http import HttpResponse
        from docx import Document
        from docx.shared import Inches
        import io

        partida_id = request.GET.get('partida')
        programa_id = request.GET.get('programa_analitico')
        unidad_id = request.GET.get('unidad')

        if not partida_id:
            return JsonResponse({'success': False, 'error': 'Partida requerida'}, status=400)

        # Obtener datos (similar a obtener_prompt)
        partida = PartidaRepository.get_by_id(int(partida_id))
        if not partida:
            return JsonResponse({'success': False, 'error': 'Partida no encontrada'}, status=404)

        asignatura = AsignaturaRepository.get_by_id(partida['asignatura_id'])
        if not asignatura:
            return JsonResponse({'success': False, 'error': 'Asignatura no encontrada'}, status=404)

        carrera = None
        if asignatura.get('carrera_id'):
            carrera = CarreraRepository.get_by_id(asignatura['carrera_id'])

        # Obtener datos de preguntas (SIN FILTRAR POR UNIDAD - TODAS LAS UNIDADES)
        unidades_data = []
        programas = ProgramaAnaliticoRepository.list_by_asignatura(
            asignatura_id=asignatura['asignatura_id']
        )

        for programa in programas:
            unidades = UnidadRepository.list_all(
                limit=1000,
                programa_analitico_id=programa['linea_educativa_id']
            )

            for unidad in unidades:
                # NO FILTRAR POR UNIDAD - INCLUIR TODAS LAS UNIDADES
                preguntas = PreguntaRepository.list_all(limit=1000, unidad_id=unidad['unidad_id'])

                unidad_info = {
                    'numero': unidad['numero_unidad'],
                    'descripcion': unidad['descripcion'],
                    'preguntas': []
                }

                for pregunta in preguntas:
                    opciones = OpcionRepository.list_all(limit=1000, pregunta_id=pregunta['pregunta_id'])

                    pregunta_info = {
                        'numero': pregunta['numero'],
                        'enunciado': pregunta['enunciado'],
                        'opciones': []
                    }

                    for opcion in opciones:
                        pregunta_info['opciones'].append({
                            'texto': opcion['opcion'],
                            'es_correcta': opcion['es_correcta']
                        })

                    unidad_info['preguntas'].append(pregunta_info)

                if unidad_info['preguntas']:
                    unidades_data.append(unidad_info)

        # Generar documento Word
        doc = generar_documento_word(partida, asignatura, carrera, unidades_data)

        # Crear respuesta HTTP
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="preguntas_{partida["descripcion"]}.docx"'

        # Guardar documento en memoria
        doc_buffer = io.BytesIO()
        doc.save(doc_buffer)
        doc_buffer.seek(0)

        response.write(doc_buffer.getvalue())
        return response

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def generar_prompt_texto(partida, asignatura, carrera, programas, unidades_data, unidad_actual=None):
    """Generar texto del prompt para IA con formato específico"""

    # Obtener programa analítico (usar el primero si hay varios)
    programa = programas[0] if programas else {}

    # Construir lista de unidades con número de preguntas
    unidades_lista = []
    for unidad in unidades_data:
        unidades_lista.append({
            "numero": unidad['numero'],
            "descripcion": unidad['descripcion'],
            "num_preguntas": len(unidad['preguntas'])
        })

    # Si hay unidad actual específica, agregar información adicional
    unidad_info_extra = ""
    if unidad_actual:
        unidad_info_extra = f"""
            INFORMACIÓN DE UNIDAD ESPECÍFICA:
            - Unidad actual: {unidad_actual['numero']} — {unidad_actual['descripcion']}
            - Enfócate en esta unidad específica para generar las preguntas.
            - Extrae los temas/subtemas del Contexto del plan que correspondan a esta unidad.
            """

    # Generar el prompt con el formato específico
    prompt = f"""ROL
Eres un reclutador de docentes de universidad de élite. Debes evaluar un concurso observando cómo enseñan y cómo se desempeñan con preguntas claras, de dificultad baja–media, enfocadas en conceptos fundamentales y su aplicación directa.

ENTRADAS
- Carrera: {carrera['descripcion'] if carrera else 'No especificada'}
- Programa: {asignatura['descripcion']}
- Asignatura: {asignatura['descripcion']}
- Plan analítico (título): {programa.get('titulo', 'No especificado')}
- Contexto del plan: {programa.get('contexto', 'No especificado')}  ← aquí se listan los temas y subtemas por unidad; úsalos como base obligatoria
- Unidades (lista con número, descripción y # de preguntas):
{unidades_lista}{unidad_info_extra}

OBJETIVO
Para cada unidad, genera EXACTAMENTE el número de preguntas solicitado, tipo **caso breve de estudio (nivel universitario)**, con **una sola respuesta correcta** por pregunta. Cada caso debe alinearse explícitamente con **un tema/subtema** de esa unidad indicado en el **Contexto del plan**.

IMPORTANTE - EXTRACCIÓN DE TEMAS/SUBTEMAS:
- Los temas y subtemas para cada pregunta DEBEN extraerse del "Contexto del plan" mostrado arriba
- Cada unidad tiene sus temas específicos listados en el contexto
- NO inventes temas, usa SOLO los que aparecen en el contexto para cada unidad
- Los temas/subtemas deben ser específicos de la unidad correspondiente

ESTRUCTURA DE CADA PREGUNTA (formato específico)
- **Narración del caso (2–4 líneas):** escenario realista y corto (laboratorio, aula, empresa, servicio público, clínica, etc.) que conecte con un **tema/subtema** de la unidad.
- **Pregunta directa (1 línea):** compara, identifica o aplica un concepto clave del **tema/subtema**.
- **Opciones (A–D):** cuatro opciones, **solo una correcta**. Distractores plausibles, sin trucos rebuscados.
- **Respuesta correcta:** letra de la opción correcta.
- **Explicación (1–2 líneas):** razón breve de por qué es correcta y por qué las otras no.
- **Metadatos por ítem (cortos):**
- Carrera: {carrera['descripcion'] if carrera else 'No especificada'} · Programa: {asignatura['descripcion']}
- Asignatura: {asignatura['descripcion']}
- Unidad: [Usar los datos reales de las unidades listadas abajo]
- Tema/Subtema: [EXTRAER DEL CONTEXTO DEL PLAN - NO INVENTAR]
  - Dificultad: [[baja|media]]

REQUISITOS DE CALIDAD (EN TODO EL SET)
- Lenguaje claro y didáctico; evita tecnicismos innecesarios.
- **Cobertura balanceada:** usa todos los temas/subtemas del Contexto para esa unidad (si sobran preguntas, repite con enfoque distinto).
- **Dificultad global:** ~70% baja y ~30% media. No incluir preguntas de alta dificultad.
- **Enfoque conceptual:** una idea central por pregunta (definición, diferencia clave, identificación, aplicación directa).
- **Escenarios breves y variados**, pero simples; sin cálculos extensos ni información ambigua.
- **Distractores** basados en confusiones comunes; no uses redacciones capciosas.
- Longitud por ítem (sin metadatos): **60–120 palabras**.
- **Una sola** opción correcta; no repetir la respuesta con sinónimos en otras opciones.
- Referenciar explícitamente la **Unidad** y el **Tema/Subtema** en cada ítem.

FORMATO DE SALIDA (formato específico, uno por pregunta)
Pregunta [[#]]
[[Narración del caso - 2-4 líneas]]
[[Pregunta directa - 1 línea]]
Opciones:
a) [[...]]
b) [[...]]
c) [[...]]
d) [[...]]
Respuesta correcta: [[letra]]
Explicación: [[1-2 líneas]]

Metadatos:
- Unidad: [Usar los datos reales de las unidades listadas abajo]
- Tema/Subtema: [Extraer del Contexto del plan]
- Dificultad: [[baja|media]]

DATOS REALES DE LAS UNIDADES DISPONIBLES:
"""

    # Agregar datos reales de las unidades
    for unidad in unidades_data:
        prompt += f"- Unidad {unidad['numero']}: {unidad['descripcion']}\n"

    prompt += """

INSTRUCCIONES ESPECÍFICAS PARA TEMAS/SUBTEMAS:
1. Revisa el "Contexto del plan" mostrado arriba
2. Identifica los temas y subtemas listados para cada unidad
3. Para cada pregunta, usa UNO de esos temas/subtemas específicos
4. NO inventes temas que no estén en el contexto
5. Cada unidad debe tener preguntas basadas en SUS temas específicos del contexto

EJEMPLO DE METADATOS CORRECTOS (usar los datos reales de arriba):
- Unidad: 1 — Generalidades de la Ingeniería Genética
- Unidad: 2 — Técnicas de Clonación Molecular
- Unidad: 3 — Aplicaciones en Biotecnología
- etc.

AL FINAL (por unidad)
Incluye un **Resumen de la Unidad** (3–5 bullets) con: temas/subtemas cubiertos (según el Contexto del plan), distribución baja–media, y variedad básica de escenarios.

---

"""
    return prompt


def generar_documento_word(partida, asignatura, carrera, unidades_data):
    """Generar documento Word con formato simple y limpio"""
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    import os

    doc = Document()

    # Configurar márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Crear encabezado solo con logo UNEMI
    def add_header_with_logo(doc_obj):
        section = doc_obj.sections[0]
        header = section.header

        # Solo agregar el logo en el encabezado
        logo_path = os.path.join('app', 'static', 'img', 'unemi.png')
        if os.path.exists(logo_path):
            try:
                logo_paragraph = header.paragraphs[0]
                logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = logo_paragraph.add_run()
                run.add_picture(logo_path, width=Inches(1.5))
            except Exception:
                # Si no se puede cargar la imagen, usar texto
                logo_paragraph = header.paragraphs[0]
                logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                logo_run = logo_paragraph.add_run('UNEMI')
                logo_run.bold = True
                logo_run.font.size = Pt(16)
        else:
            # Usar texto si no hay logo
            logo_paragraph = header.paragraphs[0]
            logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            logo_run = logo_paragraph.add_run('UNEMI')
            logo_run.bold = True
            logo_run.font.size = Pt(16)

    # Agregar encabezado
    add_header_with_logo(doc)

    # Agregar tabla de información de carrera y asignatura
    def add_info_table(doc_obj, carrera_obj, asignatura_obj):
        from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
        from docx.shared import Cm

        # Crear tabla con 2 filas y 2 columnas
        table = doc_obj.add_table(rows=2, cols=2)
        table.style = 'Table Grid'

        # Configurar propiedades de la tabla
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        table.left_indent = Cm(0)  # Sangría izquierda: 0 cm

        # Configurar ancho de columnas (12.356 cm total)
        table.columns[0].width = Cm(2.0)      # Columna izquierda (CARRERA, ASIGNATURA)
        table.columns[1].width = Cm(10.356)   # Columna derecha (valores)

        # Configurar altura mínima de filas (0.749 cm)
        for row in table.rows:
            row.height = Cm(0.749)
            row.height_rule = 'at_least'  # Altura mínima

        # Configurar propiedades de celdas
        for row in table.rows:
            for cell in row.cells:
                # Alineación vertical: Parte superior
                cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP

        # Primera fila - CARRERA
        row1 = table.rows[0]
        row1.cells[0].text = 'CARRERA'
        row1.cells[1].text = carrera_obj['descripcion'] if carrera_obj else 'No especificada'

        # Segunda fila - ASIGNATURA
        row2 = table.rows[1]
        row2.cells[0].text = 'ASIGNATURA'
        row2.cells[1].text = asignatura_obj['descripcion']

        # Aplicar formato a todas las celdas
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
                        run.font.size = Pt(11)
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Agregar espacio después de la tabla
        doc_obj.add_paragraph()

    # Agregar tabla de información
    add_info_table(doc, carrera, asignatura)

    # Contador global de preguntas para numeración continua
    contador_pregunta_global = 1

    # Preguntas por unidad
    for unidad in unidades_data:
        # Título de la unidad (sin color)
        unidad_heading = doc.add_heading(f'UNIDAD {unidad["numero"]}: {unidad["descripcion"]}', level=1)
        unidad_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        # Quitar cualquier formato de color
        for run in unidad_heading.runs:
            run.font.color.rgb = None

        # Preguntas de la unidad
        for pregunta in unidad['preguntas']:
            # Usar numeración continua global
            pregunta_paragraph = doc.add_paragraph()
            pregunta_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pregunta_run = pregunta_paragraph.add_run(f'Pregunta {contador_pregunta_global}')
            pregunta_run.bold = True
            pregunta_run.font.size = Pt(12)

            # Enunciado de la pregunta
            enunciado_paragraph = doc.add_paragraph()
            enunciado_paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            enunciado_run = enunciado_paragraph.add_run(pregunta['enunciado'])
            enunciado_run.font.size = Pt(11)

            # Opciones
            opciones_heading = doc.add_paragraph()
            opciones_heading.add_run('Opciones:')
            opciones_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

            for i, opcion in enumerate(pregunta['opciones'], 1):
                opcion_paragraph = doc.add_paragraph()
                opcion_paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                opcion_paragraph.paragraph_format.left_indent = Inches(0.3)

                letra = chr(96 + i)  # a, b, c, d
                opcion_text = f'{letra}) {opcion["texto"]}'
                opcion_run = opcion_paragraph.add_run(opcion_text)
                opcion_run.font.size = Pt(11)

                if opcion['es_correcta']:
                    opcion_run.bold = True

            # Respuesta correcta
            respuesta_paragraph = doc.add_paragraph()
            respuesta_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            respuesta_paragraph.paragraph_format.left_indent = Inches(0.3)

            # Encontrar la respuesta correcta
            for i, opcion in enumerate(pregunta['opciones'], 1):
                if opcion['es_correcta']:
                    letra_correcta = chr(96 + i)
                    respuesta_run = respuesta_paragraph.add_run(f'Respuesta correcta: {letra_correcta}')
                    respuesta_run.bold = True
                    respuesta_run.font.size = Pt(11)
                    break

            # Incrementar contador global
            contador_pregunta_global += 1

            # Espacio entre preguntas
            doc.add_paragraph()

    return doc


# ============================================================================
# VISTA PARA CREAR PARTIDAS COMPLETAS - SUPABASE
# ============================================================================

class CrearPartidaCompletaView(View):
    """Vista para crear partida completa con programa analítico y unidades - Supabase"""

    def post(self, request):
        try:
            # Obtener datos del formulario
            descripcion = request.POST.get('descripcion', '').strip()
            asignatura_id = request.POST.get('asignatura')
            titulo_programa = request.POST.get('titulo_programa', '').strip()
            contexto = request.POST.get('contexto', '').strip()
            num_unidades = int(request.POST.get('num_unidades', 0))
            preguntas_por_unidad = int(request.POST.get('preguntas_por_unidad', 10))

            # Validaciones básicas
            if not all([descripcion, asignatura_id, titulo_programa, contexto, num_unidades]):
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('partida_lista')

            # 1. Crear la partida
            partida = PartidaRepository.create(
                descripcion=descripcion,
                asignatura_id=int(asignatura_id)
            )

            if not partida:
                messages.error(request, 'Error al crear la partida')
                return redirect('partida_lista')

            # 2. Crear el programa analítico
            programa = ProgramaAnaliticoRepository.create(
                titulo=titulo_programa,
                contexto=contexto,
                asignatura_id=int(asignatura_id)
            )

            if not programa:
                messages.error(request, 'Error al crear el programa analítico')
                return redirect('partida_lista')

            # 3. Crear las unidades
            unidades_creadas = []
            for i in range(1, num_unidades + 1):
                descripcion_unidad = request.POST.get(f'unidad_{i}_descripcion', '').strip()
                if descripcion_unidad:
                    unidad = UnidadRepository.create(
                        numero_unidad=i,
                        descripcion=descripcion_unidad,
                        num_preguntas=preguntas_por_unidad,
                        programa_analitico_id=programa['linea_educativa_id']
                    )
                    if unidad:
                        unidades_creadas.append(unidad)

            # 4. Crear preguntas automáticas para cada unidad con numeración secuencial
            preguntas_creadas = 0
            contador_pregunta_global = 1  # Contador global para numeración secuencial

            for unidad in unidades_creadas:
                for _ in range(preguntas_por_unidad):
                    pregunta = PreguntaRepository.create(
                        numero=contador_pregunta_global,  # Usar contador global
                        enunciado=f"Pregunta {contador_pregunta_global}",
                        unidad_id=unidad['unidad_id']
                    )
                    if pregunta:
                        # Crear opciones para la pregunta
                        for k in range(1, 5):  # 4 opciones por pregunta
                            es_correcta = (k == 1)  # La primera opción es correcta por defecto
                            OpcionRepository.create(
                                opcion=f"Opción {k} para pregunta {contador_pregunta_global}",
                                es_correcta=es_correcta,
                                pregunta_id=pregunta['pregunta_id']
                            )
                        preguntas_creadas += 1
                        contador_pregunta_global += 1  # Incrementar contador global

            # Mensaje de éxito
            messages.success(
                request,
                f'¡Partida creada exitosamente! '
                f'Se crearon {len(unidades_creadas)} unidades y {preguntas_creadas} preguntas automáticamente.'
            )

            return redirect('partida_lista')

        except Exception as e:
            messages.error(request, f'Error al crear la partida: {str(e)}')
            return redirect('partida_lista')
