from django.urls import path
from . import views

urlpatterns = [
    # ============================================================================
    # PÁGINAS PRINCIPALES - SUPABASE
    # ============================================================================
    path('', views.PartidaListView.as_view(), name='partida_lista'),
    path('crear-partida/', views.CrearPartidaCompletaView.as_view(), name='crear_partida_completa'),
    path('unidades/', views.UnidadListView.as_view(), name='unidad_lista'),
    path('preguntas/', views.PreguntaListView.as_view(), name='pregunta_lista'),
    
    # ============================================================================
    # APIs DE EDICIÓN INLINE - SUPABASE
    # ============================================================================
    path('api/partidas/<int:partida_id>/update/', views.update_partida_api, name='update_partida_api'),
    path('api/unidades/<int:unidad_id>/update/', views.update_unidad_api, name='update_unidad_api'),
    path('api/preguntas/<int:pregunta_id>/update/', views.update_pregunta_api, name='update_pregunta_api'),
    path('api/opciones/<int:opcion_id>/delete/', views.delete_opcion_api, name='delete_opcion_api'),
    
    # ============================================================================
    # APIs DE CREACIÓN - SUPABASE
    # ============================================================================
    path('api/crear-carrera/', views.crear_carrera_ajax, name='crear_carrera_ajax'),
    path('api/crear-asignatura/', views.crear_asignatura_ajax, name='crear_asignatura_ajax'),
    
    # ============================================================================
    # APIs DE FILTROS DINÁMICOS - SUPABASE
    # ============================================================================
    path('api/programas-analiticos/', views.get_programas_analiticos, name='get_programas_analiticos'),
    path('api/unidades/', views.get_unidades, name='get_unidades'),
    
    # ============================================================================
    # APIs DE GENERACIÓN DE CONTENIDO - SUPABASE
    # ============================================================================
    path('api/obtener-prompt/', views.obtener_prompt, name='obtener_prompt'),
    path('api/descargar-google-docs/', views.descargar_google_docs, name='descargar_google_docs'),
]