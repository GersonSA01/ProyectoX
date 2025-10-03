from typing import Any, Dict, List, Optional, Tuple

from .supabase_client import get_supabase_client


class CarreraRepository:
    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        res = client.table("carrera").select("carrera_id, descripcion").limit(limit).offset(offset).execute()
        return res.data or []

    @staticmethod
    def get_by_id(carrera_id: int) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        res = client.table("carrera").select("carrera_id, descripcion").eq("carrera_id", carrera_id).single().execute()
        return res.data

    @staticmethod
    def create(descripcion: str) -> Dict[str, Any]:
        client = get_supabase_client()
        res = client.table("carrera").insert({"descripcion": descripcion}).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def update(carrera_id: int, descripcion: Optional[str] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        patch: Dict[str, Any] = {}
        if descripcion is not None:
            patch["descripcion"] = descripcion
        res = client.table("carrera").update(patch).eq("carrera_id", carrera_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def delete(carrera_id: int) -> Tuple[int, Optional[Dict[str, Any]]]:
        client = get_supabase_client()
        res = client.table("carrera").delete().eq("carrera_id", carrera_id).execute()
        return (1, res.data[0] if res.data else None)


class AsignaturaRepository:
    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        query = (
            client.table("asignatura")
            .select("asignatura_id, descripcion, carrera_id")
            .limit(limit).offset(offset)
        )
        res = query.execute()
        return res.data or []

    @staticmethod
    def get_by_id(asignatura_id: int) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        res = (
            client.table("asignatura")
            .select("asignatura_id, descripcion, carrera_id")
            .eq("asignatura_id", asignatura_id)
            .single()
            .execute()
        )
        return res.data

    @staticmethod
    def find_by_descripcion_ilike(descripcion: str) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        res = client.table("asignatura").select("*").ilike("descripcion", descripcion).execute()
        return res.data or []

    @staticmethod
    def create(descripcion: str, carrera_id: Optional[int]) -> Dict[str, Any]:
        client = get_supabase_client()
        payload = {"descripcion": descripcion, "carrera_id": carrera_id}
        res = client.table("asignatura").insert(payload).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def update(asignatura_id: int, descripcion: Optional[str] = None, carrera_id: Optional[int] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        patch: Dict[str, Any] = {}
        if descripcion is not None:
            patch["descripcion"] = descripcion
        if carrera_id is not None:
            patch["carrera_id"] = carrera_id
        res = (
            client.table("asignatura")
            .update(patch)
            .eq("asignatura_id", asignatura_id)
            .execute()
        )
        return res.data[0] if res.data else None

    @staticmethod
    def delete(asignatura_id: int) -> Tuple[int, Optional[Dict[str, Any]]]:
        client = get_supabase_client()
        res = (
            client.table("asignatura")
            .delete()
            .eq("asignatura_id", asignatura_id)
            .execute()
        )
        return (1, res.data[0] if res.data else None)


class ProgramaAnaliticoRepository:
    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        res = client.table("programaanalitico").select("linea_educativa_id, titulo, contexto, asignatura_id").limit(limit).offset(offset).execute()
        return res.data or []

    @staticmethod
    def get_by_id(linea_educativa_id: int) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        res = client.table("programaanalitico").select("*").eq("linea_educativa_id", linea_educativa_id).single().execute()
        return res.data

    @staticmethod
    def list_by_asignatura(asignatura_id: int, limit: int = 1000) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        res = (
            client.table("programaanalitico")
            .select("linea_educativa_id, titulo, contexto, asignatura_id")
            .eq("asignatura_id", asignatura_id)
            .limit(limit)
            .execute()
        )
        return res.data or []

    @staticmethod
    def create(titulo: str, contexto: str, asignatura_id: int) -> Dict[str, Any]:
        client = get_supabase_client()
        payload = {"titulo": titulo, "contexto": contexto, "asignatura_id": asignatura_id}
        res = client.table("programaanalitico").insert(payload).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def update(linea_educativa_id: int, titulo: Optional[str] = None, contexto: Optional[str] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        patch: Dict[str, Any] = {}
        if titulo is not None:
            patch["titulo"] = titulo
        if contexto is not None:
            patch["contexto"] = contexto
        res = client.table("programaanalitico").update(patch).eq("linea_educativa_id", linea_educativa_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def delete(linea_educativa_id: int) -> Tuple[int, Optional[Dict[str, Any]]]:
        client = get_supabase_client()
        res = client.table("programaanalitico").delete().eq("linea_educativa_id", linea_educativa_id).execute()
        return (1, res.data[0] if res.data else None)


class UnidadRepository:
    @staticmethod
    def list_all(limit: int = 100, offset: int = 0, programa_analitico_id: Optional[int] = None) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        query = client.table("unidad").select("unidad_id, numero_unidad, descripcion, num_preguntas, programa_analitico_id")
        if programa_analitico_id is not None:
            query = query.eq("programa_analitico_id", programa_analitico_id)
        res = query.limit(limit).offset(offset).execute()
        return res.data or []

    @staticmethod
    def get_by_id(unidad_id: int) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        res = client.table("unidad").select("*").eq("unidad_id", unidad_id).single().execute()
        return res.data

    @staticmethod
    def create(numero_unidad: int, descripcion: str, num_preguntas: int, programa_analitico_id: int) -> Dict[str, Any]:
        client = get_supabase_client()
        payload = {
            "numero_unidad": numero_unidad,
            "descripcion": descripcion,
            "num_preguntas": num_preguntas,
            "programa_analitico_id": programa_analitico_id,
        }
        res = client.table("unidad").insert(payload).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def update(unidad_id: int, descripcion: Optional[str] = None, numero_unidad: Optional[int] = None, num_preguntas: Optional[int] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        patch: Dict[str, Any] = {}
        if descripcion is not None:
            patch["descripcion"] = descripcion
        if numero_unidad is not None:
            patch["numero_unidad"] = numero_unidad
        if num_preguntas is not None:
            patch["num_preguntas"] = num_preguntas
        res = client.table("unidad").update(patch).eq("unidad_id", unidad_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def delete(unidad_id: int) -> Tuple[int, Optional[Dict[str, Any]]]:
        client = get_supabase_client()
        res = client.table("unidad").delete().eq("unidad_id", unidad_id).execute()
        return (1, res.data[0] if res.data else None)


class PreguntaRepository:
    @staticmethod
    def list_all(limit: int = 100, offset: int = 0, unidad_id: Optional[int] = None) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        query = client.table("pregunta").select("pregunta_id, enunciado, explicacion, numero, unidad_id")
        if unidad_id is not None:
            query = query.eq("unidad_id", unidad_id)
        res = query.limit(limit).offset(offset).execute()
        return res.data or []

    @staticmethod
    def create(enunciado: str, numero: int, unidad_id: int, explicacion: Optional[str] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        payload = {"enunciado": enunciado, "numero": numero, "unidad_id": unidad_id}
        if explicacion:
            payload["explicacion"] = explicacion
        res = client.table("pregunta").insert(payload).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def update(pregunta_id: int, enunciado: Optional[str] = None, numero: Optional[int] = None, explicacion: Optional[str] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        patch: Dict[str, Any] = {}
        if enunciado is not None:
            patch["enunciado"] = enunciado
        if numero is not None:
            patch["numero"] = numero
        if explicacion is not None:
            patch["explicacion"] = explicacion
        res = client.table("pregunta").update(patch).eq("pregunta_id", pregunta_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def delete(pregunta_id: int) -> Tuple[int, Optional[Dict[str, Any]]]:
        client = get_supabase_client()
        res = client.table("pregunta").delete().eq("pregunta_id", pregunta_id).execute()
        return (1, res.data[0] if res.data else None)


class OpcionRepository:
    @staticmethod
    def list_all(limit: int = 100, offset: int = 0, pregunta_id: Optional[int] = None) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        query = client.table("opcion").select("opcion_id, opcion, media_url, es_correcta, pregunta_id")
        if pregunta_id is not None:
            query = query.eq("pregunta_id", pregunta_id)
        res = query.limit(limit).offset(offset).execute()
        return res.data or []

    @staticmethod
    def create(opcion: str, es_correcta: bool, pregunta_id: int, media_url: Optional[str] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        payload: Dict[str, Any] = {"opcion": opcion, "es_correcta": es_correcta, "pregunta_id": pregunta_id}
        if media_url is not None:
            payload["media_url"] = media_url
        res = client.table("opcion").insert(payload).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def update(opcion_id: int, opcion: Optional[str] = None, es_correcta: Optional[bool] = None, media_url: Optional[str] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        patch: Dict[str, Any] = {}
        if opcion is not None:
            patch["opcion"] = opcion
        if es_correcta is not None:
            patch["es_correcta"] = es_correcta
        if media_url is not None:
            patch["media_url"] = media_url
        res = client.table("opcion").update(patch).eq("opcion_id", opcion_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def delete(opcion_id: int) -> Tuple[int, Optional[Dict[str, Any]]]:
        client = get_supabase_client()
        res = client.table("opcion").delete().eq("opcion_id", opcion_id).execute()
        return (1, res.data[0] if res.data else None)


class PartidaRepository:
    @staticmethod
    def list_all(limit: int = 100, offset: int = 0, asignatura_id: Optional[int] = None) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        query = client.table("partida").select("partida_id, descripcion, asignatura_id")
        if asignatura_id is not None:
            query = query.eq("asignatura_id", asignatura_id)
        res = query.limit(limit).offset(offset).execute()
        return res.data or []

    @staticmethod
    def create(descripcion: str, asignatura_id: int) -> Dict[str, Any]:
        client = get_supabase_client()
        payload = {"descripcion": descripcion, "asignatura_id": asignatura_id}
        res = client.table("partida").insert(payload).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def get_by_id(partida_id: int) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        res = client.table("partida").select("*").eq("partida_id", partida_id).single().execute()
        return res.data

    @staticmethod
    def update(partida_id: int, descripcion: Optional[str] = None) -> Dict[str, Any]:
        client = get_supabase_client()
        patch: Dict[str, Any] = {}
        if descripcion is not None:
            patch["descripcion"] = descripcion
        res = client.table("partida").update(patch).eq("partida_id", partida_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def delete(partida_id: int) -> Tuple[int, Optional[Dict[str, Any]]]:
        client = get_supabase_client()
        res = client.table("partida").delete().eq("partida_id", partida_id).execute()
        return (1, res.data[0] if res.data else None)


