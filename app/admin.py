from django.contrib import admin

from .models import Asignatura, Pregunta, Opcion, Unidad, ProgramaAnalitico, Partida, Carrera

admin.site.register(Asignatura)
admin.site.register(Pregunta)
admin.site.register(Opcion)
admin.site.register(Unidad)
admin.site.register(ProgramaAnalitico)
admin.site.register(Partida)
admin.site.register(Carrera)