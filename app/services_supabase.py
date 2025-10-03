from typing import Dict, Any, List

from .repositories import (
    PartidaRepository,
    ProgramaAnaliticoRepository,
    UnidadRepository,
    PreguntaRepository,
    OpcionRepository,
    AsignaturaRepository,
)


class SupabaseBusinessService:
    @staticmethod
    def crear_partida_con_programa_y_unidades(
        descripcion_partida: str,
        asignatura_id: int,
        titulo_programa: str,
        contexto: str,
        num_unidades: int,
        preguntas_por_unidad: int,
        unidades_personalizadas: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        partida = PartidaRepository.create(descripcion_partida, asignatura_id)

        programa = ProgramaAnaliticoRepository.create(
            titulo=titulo_programa,
            contexto=contexto or "",
            asignatura_id=asignatura_id,
        )

        unidades_creadas: List[Dict[str, Any]] = []
        for i in range(1, int(num_unidades) + 1):
            if unidades_personalizadas and len(unidades_personalizadas) >= i:
                u_cfg = unidades_personalizadas[i - 1]
                numero = int(u_cfg.get("numero", i))
                descripcion = u_cfg.get("descripcion", f"Unidad {i}")
                n_pregs = int(u_cfg.get("num_preguntas", preguntas_por_unidad))
            else:
                numero = i
                descripcion = f"Unidad {i}"
                n_pregs = int(preguntas_por_unidad)

            unidad = UnidadRepository.create(
                numero_unidad=numero,
                descripcion=descripcion,
                num_preguntas=n_pregs,
                programa_analitico_id=programa["linea_educativa_id"],
            )
            unidades_creadas.append(unidad)

            SupabaseBusinessService.generar_preguntas_basicas_para_unidad(
                unidad_id=unidad["unidad_id"],
                numero_inicio=1,
                cantidad=n_pregs,
                descripcion_unidad=descripcion,
            )

        return {
            "partida": partida,
            "programa": programa,
            "unidades": unidades_creadas,
        }

    @staticmethod
    def generar_preguntas_basicas_para_unidad(
        unidad_id: int,
        numero_inicio: int,
        cantidad: int,
        descripcion_unidad: str,
    ) -> int:
        for i in range(cantidad):
            numero_pregunta = numero_inicio + i
            enunciado = f"Pregunta {numero_pregunta} sobre {descripcion_unidad}. Explique detalladamente."
            pregunta = PreguntaRepository.create(
                enunciado=enunciado,
                numero=numero_pregunta,
                unidad_id=unidad_id,
            )

            opciones_basicas = [
                f"Opción correcta para {descripcion_unidad}",
                f"Opción parcial para {descripcion_unidad}",
                f"Opción incorrecta relacionada con {descripcion_unidad}",
                f"Opción no relacionada con {descripcion_unidad}",
            ]
            for j, opcion_texto in enumerate(opciones_basicas):
                OpcionRepository.create(
                    opcion=opcion_texto,
                    es_correcta=(j == 0),
                    pregunta_id=pregunta["pregunta_id"],
                )
        return cantidad


